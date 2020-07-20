import graphene

from chowkidar.auth import get_user_from_credentials
from chowkidar.utils import generate_token_from_claims, generate_refresh_token


class GenerateTokenResponse(graphene.ObjectType):
    payload = graphene.String(description='Payload carried in the JWT')
    token = graphene.String(description='JWT token')
    refreshToken = graphene.String(description='JWT refresh token')


class GenerateToken(graphene.Mutation, description='Authenticates an user with credentials and issues tokens'):
    class Arguments:
        email = graphene.String(required=False, description='Email address of the user.')
        username = graphene.String(required=False, description='Username of the user')
        password = graphene.String(required=True, description='Password of the user')

    Output = GenerateTokenResponse

    @staticmethod
    def mutate(self, info, password: str, email: str = None, username: str = None):
        request = info.context
        user = get_user_from_credentials(password=password, email=email, username=username, request=request)
        refreshToken = generate_refresh_token(user=user)
        data = generate_token_from_claims(claims={
            'username': user.username, 'origIat': refreshToken.created.timestamp(),
        })
        return {
            "payload": data['payload'],
            "token": data['token'],
            "refreshToken": refreshToken.get_token()
        }


class RefreshToken(graphene.Mutation):
    class Arguments:
        refreshToken = graphene.String(required=False, description='Refresh token')

    Output = GenerateTokenResponse

    @classmethod
    def mutate(cls, *args, **kwargs):
        return False


class VerifyToken(graphene.Mutation):
    class Arguments:
        token = graphene.String()
        refreshToken = graphene.String()

    Output = GenerateTokenResponse

    @classmethod
    def mutate(cls, *args, **kwargs):
        return False


class RevokeToken(graphene.Mutation):
    class Arguments:
        refreshToken = graphene.String(required=False, description='Refresh token')

    Output = GenerateTokenResponse

    @classmethod
    def mutate(cls, *args, **kwargs):
        return False


__all__ = [
    'GenerateToken',
    'RefreshToken',
    'VerifyToken',
    'RevokeToken'
]
