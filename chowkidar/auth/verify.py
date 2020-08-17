from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import RefreshToken
from ..settings import JWT_REFRESH_TOKEN_EXPIRATION_DELTA
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
            if 'JWT_REFRESH_TOKEN' in request.COOKIES:
                rf = request.COOKIES["JWT_REFRESH_TOKEN"]
                try:
                    refreshToken = verify_refresh_token(token=rf)
                    return refreshToken.user
                except Exception:
                    pass
            pass
    return None


def verify_refresh_token(token: str) -> RefreshToken:
    try:
        token = RefreshToken.objects.get(token=token, revoked__isnull=True)
        if timezone.now() > token.issued + JWT_REFRESH_TOKEN_EXPIRATION_DELTA:
            raise AuthError('Refresh Token Expired', code='EXPIRED_REFRESH_TOKEN')
        return token
    except RefreshToken.DoesNotExist:
        raise AuthError('Invalid Refresh Token', code='INVALID_REFRESH_TOKEN')


__all__ = [
    'verify_refresh_token',
    'resolve_user_from_request',
]
