from ariadne.objects import MutationType
from chowkidar.utils import AuthError

from social_core.exceptions import MissingBackend
from social_django.views import _do_login
from social_django.utils import load_backend, load_strategy


social_auth_mutations = MutationType()


@social_auth_mutations.field('socialAuth')
def authenticate_using_social_auth(_, info, accessToken, provider):
    try:
        strategy = load_strategy(info.context.request)
        backend = load_backend(strategy, provider, redirect_uri=None)
    except MissingBackend:
        raise AuthError('Auth Provider Not Supported', code='INVALID_PROVIDER')

    user = backend.do_auth(accessToken, user=None)
    _do_login(backend, user, user.social_user)
    return {"success": True, "user": user.__dict__}


__all__ = [
    'social_auth_mutations'
]
