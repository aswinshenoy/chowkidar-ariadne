from django.utils import timezone
from datetime import datetime
from django.http import HttpRequest, JsonResponse
from django.contrib.auth import get_user_model

from ..settings import JWT_REFRESH_TOKEN_EXPIRATION_DELTA, JWT_EXPIRATION_DELTA
from ..utils import generate_refresh_token, generate_token_from_claims, decode_payload_from_token
from ..utils.cookie import set_cookie

UserModel = get_user_model()


def respond_handling_authentication(
    request: HttpRequest, result: object, status_code
) -> JsonResponse:

    # Refresh Token automatically if token exists
    if 'JWT_REFRESH_TOKEN' in request.COOKIES:
        refreshToken = request.COOKIES["JWT_REFRESH_TOKEN"]
        if 'JWT_TOKEN' in request.COOKIES:
            token = request.COOKIES['JWT_TOKEN']
            try:
                payload = decode_payload_from_token(token=token)
                expiry = datetime.fromtimestamp(payload['exp'])
                now = datetime.now()
                if expiry > now + (JWT_EXPIRATION_DELTA/2):
                    resp = JsonResponse(result, status=status_code)
                    return resp
            except Exception:
                pass
        from .verify import verify_refresh_token
        try:
            rt = verify_refresh_token(refreshToken)
            data = generate_token_from_claims(claims={
                'userID': rt.user.id, 'username': rt.user.username, 'origIat': rt.issued.timestamp(),
            })
            JWTExpiry = datetime.fromtimestamp(data['payload']['exp'])
            resp = JsonResponse(result, status=status_code)
            resp = set_cookie(
                key='JWT_TOKEN', value=data['token'],
                expires=JWTExpiry, response=resp
            )
            return resp
        except Exception:
            #@todo delete all JWT Tokens
            pass

    # Issue Token if query is tokenCreate and successful
    if status_code == 200 and result['data']:
        if (
            'tokenCreate' in result['data'] and
            result['data']['tokenCreate']['success'] and
            result['data']['tokenCreate']['user']['id']
        ):
            user = UserModel.objects.get(id=result['data']['tokenCreate']['user']['id'])
            refreshToken = generate_refresh_token(user=user)
            data = generate_token_from_claims(claims={
                'userID': user.id, 'username': user.username, 'origIat': refreshToken.issued.timestamp(),
            })
            refreshExpiresIn = timezone.now() + JWT_REFRESH_TOKEN_EXPIRATION_DELTA
            result['data']['tokenCreate']['payload'] = data['payload']
            result['data']['tokenCreate']['refreshExpiresIn'] = refreshExpiresIn
            resp = JsonResponse(result, status=status_code)

            # Set JWT Token
            JWTExpiry = datetime.fromtimestamp(data['payload']['exp'])
            resp = set_cookie(
                key='JWT_TOKEN',
                value=data['token'],
                expires=JWTExpiry,
                response=resp
            )
            # Set JWT Refresh Token
            resp = set_cookie(
                key='JWT_REFRESH_TOKEN',
                value=refreshToken.get_token(),
                expires=refreshExpiresIn,
                response=resp
            )
            return resp
    return JsonResponse(result, status=status_code)


__all__ = [
    'respond_handling_authentication'
]

