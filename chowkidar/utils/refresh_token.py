from chowkidar.models import RefreshToken
from django.contrib.auth import get_user_model

UserModel = get_user_model()


def generate_refresh_token(
    user: UserModel,
) -> RefreshToken:
    return RefreshToken.objects.create(user=user)


__all__ = [
    'generate_refresh_token'
]
