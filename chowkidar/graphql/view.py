import json
from typing import Any, Callable, List, Optional, Type, Union, cast

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from graphql import GraphQLSchema
from graphql.execution import MiddlewareManager

from ariadne.constants import DATA_TYPE_JSON, DATA_TYPE_MULTIPART
from ariadne.exceptions import HttpBadRequestError
from ariadne.file_uploads import combine_multipart_data
from ariadne.format_error import format_error
from ariadne.graphql import graphql_sync
from ariadne.types import (
    ContextValue,
    ErrorFormatter,
    Extension,
    GraphQLResult,
    RootValue,
    ValidationRules,
)

from ..auth import respond_handling_authentication
from ..auth.verify import resolve_user_from_request

ExtensionList = Optional[List[Type[Extension]]]
Extensions = Union[
    Callable[[Any, Optional[ContextValue]], ExtensionList], ExtensionList
]

DEFAULT_PLAYGROUND_OPTIONS = {"request.credentials": "same-origin"}


class GraphQLResolverContext:
    def __init__(self, request, user=None):
        self.request = request
        if user:
            self.user = user
        else:
            self.user = AnonymousUser


@method_decorator(csrf_exempt, name="dispatch")
class GraphQLView(TemplateView):
    http_method_names = ["get", "post", "options"]
    template_name = "playground/playground.html"
    playground_options: Optional[dict] = None
    introspection: bool = True
    schema: Optional[GraphQLSchema] = None
    context_value: Optional[ContextValue] = None
    root_value: Optional[RootValue] = None
    logger = None
    validation_rules: Optional[ValidationRules] = None
    error_formatter: Optional[ErrorFormatter] = None
    extensions: Optional[Extensions] = None
    middleware: Optional[MiddlewareManager] = None

    def get(
        self, request: HttpRequest, *args, **kwargs
    ):  # pylint: disable=unused-argument
        options = DEFAULT_PLAYGROUND_OPTIONS.copy()
        if self.playground_options:
            options.update(self.playground_options)

        return render(
            request,
            self.get_template_names(),
            {"playground_options": json.dumps(options)},
        )

    def post(
        self, request: HttpRequest, *args, **kwargs
    ):  # pylint: disable=unused-argument
        if not self.schema:
            raise ValueError("GraphQLView was initialized without schema.")

        try:
            data = self.extract_data_from_request(request)
        except HttpBadRequestError as error:
            return HttpResponseBadRequest(error.message)

        success, result = self.execute_query(request, data)
        status_code = 200 if success else 400
        return respond_handling_authentication(request=request, result=result, status_code=status_code)

    def extract_data_from_request(self, request: HttpRequest):
        content_type = request.content_type or ""
        content_type = content_type.split(";")[0]

        if content_type == DATA_TYPE_JSON:
            return self.extract_data_from_json_request(request)
        if content_type == DATA_TYPE_MULTIPART:
            return self.extract_data_from_multipart_request(request)

        raise HttpBadRequestError(
            "Posted content must be of type {} or {}".format(
                DATA_TYPE_JSON, DATA_TYPE_MULTIPART
            )
        )

    def extract_data_from_json_request(self, request: HttpRequest):
        try:
            return json.loads(request.body)
        except (TypeError, ValueError):
            raise HttpBadRequestError("Request body is not a valid JSON")

    def extract_data_from_multipart_request(self, request: HttpRequest):
        try:
            operations = json.loads(request.POST.get("operations"))
        except (TypeError, ValueError):
            raise HttpBadRequestError(
                "Request 'operations' multipart field is not a valid JSON"
            )
        try:
            files_map = json.loads(request.POST.get("map"))
        except (TypeError, ValueError):
            raise HttpBadRequestError(
                "Request 'map' multipart field is not a valid JSON"
            )

        return combine_multipart_data(operations, files_map, request.FILES)

    def execute_query(self, request: HttpRequest, data: dict) -> GraphQLResult:
        context_value = self.get_context_for_request(request)
        extensions = self.get_extensions_for_request(request, context_value)

        return graphql_sync(
            cast(GraphQLSchema, self.schema),
            data,
            context_value=context_value,
            root_value=self.root_value,
            validation_rules=self.validation_rules,
            debug=settings.DEBUG,
            introspection=self.introspection,
            logger=self.logger,
            error_formatter=self.error_formatter or format_error,
            extensions=extensions,
            middleware=self.middleware,
        )

    @staticmethod
    def get_context_for_request(request: HttpRequest) -> Optional[ContextValue]:
        user = resolve_user_from_request(request)
        return GraphQLResolverContext(
            request=request, user=user
        )

    def get_extensions_for_request(
        self, request: HttpRequest, context: Optional[ContextValue]
    ) -> ExtensionList:
        if callable(self.extensions):
            return self.extensions(request, context)  # pylint: disable=not-callable
        return self.extensions


__all__ = [
    'GraphQLView'
]
