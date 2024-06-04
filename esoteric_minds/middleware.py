from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
import jwt
from django.conf import settings
from users.models import User
from bson import ObjectId
import re
from urllib.parse import parse_qs


@database_sync_to_async
def get_user(auth_token):
    if auth_token is None:
        return None
    try:
        user_payload = jwt.decode(auth_token, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
    except (jwt.exceptions.InvalidSignatureError, jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
        return None
    else:
        user_id = user_payload.get('user_id')
        try:
            user = User.objects.get(_id=ObjectId(user_id))
        except User.DoesNotExist:
            return None
        else:
            return user


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            authorization_token = re.search(r'token=([^&]*)', str(scope['query_string']))

            if authorization_token:
                authorization_token = authorization_token.group(1).replace("'", "")
                print(authorization_token)

            if authorization_token:
                token_key = authorization_token
            else:
                token_key = None
        except ValueError:
            token_key = None

        scope['user'] = None if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)