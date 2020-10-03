from http.cookies import SimpleCookie
from typing import Optional, Callable, Any

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

from ariadne.asgi import GraphQL
from ariadne.contrib.django.views import GraphQLView as AriadneView
from ariadne.exceptions import HttpBadRequestError

from ariadne.types import ContextValue

from ..auth import respond_handling_authentication
from ..auth.verify import resolve_user_from_request, resolve_user_from_tokens

User = get_user_model()


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


# This is an ASGI2 compatibility class so that we can use ariadne subscriptions with channels.
# Once channels supports ASGI3 this class can go away:
# https://github.com/mirumee/ariadne/issues/210
class AuthenticatedChannel(GraphQL):
    def __call__(self, scope) -> Callable:
        self.scope = scope

        async def handle(receive, send):
            await super(AuthenticatedChannel, self).__call__(scope, receive, send)

        return handle

    @database_sync_to_async
    def resolve_user(self, cookie):
        return resolve_user_from_tokens(
            token=cookie['JWT_TOKEN'].value if 'JWT_TOKEN' in cookie else None,
            refreshToken=cookie['JWT_REFRESH_TOKEN'].value if 'JWT_REFRESH_TOKEN' in cookie else None
        )

    async def get_context_for_request(self, request: Any) -> Any:
        headers = dict(self.scope['headers'])
        user = AnonymousUser()
        if b'cookie' in headers:
            cookie = SimpleCookie()
            cookie.load(str(headers[b'cookie']))
            user = await self.resolve_user(cookie)
        if user is None:
            user = AnonymousUser()
        return {"request": request, "user": user}


__all__ = [
    'GraphQLView',
    'AuthenticatedChannel'
]
