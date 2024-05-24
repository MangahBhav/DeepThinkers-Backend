import jwt
from bson import ObjectId
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from esoteric_minds import (settings)
from users.models import User


class JWTAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth_token = request.headers.get('Authorization')
        if auth_token is None:
            return None
        try:
            if len(auth_token.split(' ')) != 2 or auth_token.split(' ')[0] != 'Bearer':
                raise AuthenticationFailed('Invalid Authentication token')

            token = auth_token.split(' ')[1]
            user_payload = jwt.decode(token, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
        except (jwt.exceptions.InvalidSignatureError, jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
            raise AuthenticationFailed('Invalid Authentication token')
        else:
            user_id = user_payload.get('user_id')
            try:
                user = User.objects.prefetch_related('user_blocks', 'flagged_posts').get(_id=ObjectId(user_id))
            except User.DoesNotExist:
                raise AuthenticationFailed('Invalid Authentication token')
            else:
                return user, token


def authenticate(self, auth_token):
    if auth_token is None:
        return None
    try:
        if len(auth_token.split(' ')) != 2 or auth_token.split(' ')[0] != 'Bearer':
            return None

        token = auth_token.split(' ')[1]
        user_payload = jwt.decode(token, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
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
