from django.http import HttpRequest
from django.contrib.auth import get_user_model

from ..models import RefreshToken
from ..utils import decode_payload_from_token, AuthError

UserModel = get_user_model()


def resolve_user_from_request(request: HttpRequest) -> UserModel:
    if 'JWT_TOKEN' in request.COOKIES:
        token = request.COOKIES["JWT_TOKEN"]
        try:
            payload = decode_payload_from_token(token=token)
            try:
                return UserModel.objects.get(id=payload['userID'])
            except Exception:
                pass
        except Exception:
            pass
    return None


def verify_refresh_token(token: str) -> RefreshToken:
    try:
        return RefreshToken.objects.get(token=token, revoked__isnull=True)
    except RefreshToken.DoesNotExist:
        raise AuthError('Invalid Refresh Token', code='INVALID_REFRESH_TOKEN')


__all__ = [
    'verify_refresh_token',
    'resolve_user_from_request'
]
