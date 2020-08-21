from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from ariadne.contrib.django.views import GraphQLView as AriadneView
from ariadne.exceptions import HttpBadRequestError

from ariadne.types import ContextValue


from ..auth import respond_handling_authentication
from ..auth.verify import resolve_user_from_request


class GraphQLResolverContext:
    def __init__(self, request, user=None):
        self.request = request
        self.user = user if user else AnonymousUser


@method_decorator(csrf_exempt, name="dispatch")
class GraphQLView(AriadneView):

    def post(
        self, request: HttpRequest, *args, **kwargs
    ):
        if not self.schema:
            raise ValueError("GraphQLView was initialized without schema.")

        try:
            data = self.extract_data_from_request(request)
        except HttpBadRequestError as error:
            return HttpResponseBadRequest(error.message)

        success, result = self.execute_query(request, data)
        status_code = 200 if success else 400
        return respond_handling_authentication(request=request, result=result, status_code=status_code)

    @staticmethod
    def get_context_for_request(request: HttpRequest) -> Optional[ContextValue]:
        user = resolve_user_from_request(request)
        return GraphQLResolverContext(request=request, user=user)


__all__ = [
    'GraphQLView'
]
