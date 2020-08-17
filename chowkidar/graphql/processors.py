from ariadne.objects import MutationType

from . import login_required
from ..auth import authenticate_user_from_credentials

auth_mutations = MutationType()


@auth_mutations.field('authenticateUser')
def authenticate_using_credentials(_, info, password: str, email: str = None, username: str = None):
    request = info.context.request
    user = authenticate_user_from_credentials(password=password, email=email, username=username, request=request)
    return {"success": True, "user": user}


@auth_mutations.field('logoutUser')
@login_required
def logout_user(_, info):
    return True


__all__ = [
    'auth_mutations'
]
