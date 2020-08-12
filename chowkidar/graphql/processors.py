from ariadne.objects import MutationType

from ..auth import authenticate_user_from_credentials

auth_mutations = MutationType()


@auth_mutations.field('tokenCreate')
def authenticate_using_credentials(_, info, password: str, email: str = None, username: str = None):
    request = info.context.request
    user = authenticate_user_from_credentials(password=password, email=email, username=username, request=request)
    return {"success": True, "user": user}


__all__ = [
    'auth_mutations'
]
