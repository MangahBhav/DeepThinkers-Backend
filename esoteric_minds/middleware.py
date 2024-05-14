from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
import jwt
from django.conf import settings
from users.models import User
from bson import ObjectId


@database_sync_to_async
def get_user(auth_token):
    if auth_token is None:
        return AnonymousUser
    try:
        if len(auth_token.split(' ')) != 2 or auth_token.split(' ')[0] != 'Bearer':
            return AnonymousUser

        token = auth_token.split(' ')[1]
        user_payload = jwt.decode(token, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
    except (jwt.exceptions.InvalidSignatureError, jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return AnonymousUser
    else:
        user_id = user_payload.get('user_id')
        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            return AnonymousUser
        else:
            return user


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            authorization_header = list(filter(lambda x: x[0].decode() == 'authorization', scope['headers']))
            if authorization_header:
                token_key = authorization_header[0][1].decode()
            else:
                token_key = None
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)