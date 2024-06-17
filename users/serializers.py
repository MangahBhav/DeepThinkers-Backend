from rest_framework import serializers
from django.contrib.auth import authenticate

from esoteric_minds import settings
from users.models import User, FriendRequest, Block
from bson import ObjectId, errors as bson_errors
import jwt


class UserSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(read_only=True)
    profile_image = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    added_friend = serializers.SerializerMethodField()
    blocked_user = serializers.SerializerMethodField()

    def get_added_friend(self, user):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.has_added_friend(user)
        return False

    def get_blocked_user(self, user):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.has_blocked_user(user)
        return False

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['_id', 'username', 'email', 'profile_image',
                  'added_friend', 'blocked_user', 'password', 'date', 'city', 'state', 'country', 'star']


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        users = User.objects.all()
        user = users.filter(email=email)

        if user:
            authenticated_user = authenticate(username=email, password=password)
            if not authenticated_user:
                raise serializers.ValidationError('Invalid login details provided')
            attrs['user'] = authenticated_user
            return attrs
        else:
            raise serializers.ValidationError('Invalid login details provided')


class FriendRequestSerializer(serializers.ModelSerializer):
    initiator = serializers.CharField(read_only=True)
    receiver = serializers.CharField(required=True)

    class Meta:
        model = FriendRequest
        fields = "__all__"


class BlockUserSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    blocked_user = serializers.CharField()

    class Meta:
        model = Block
        fields = "__all__"

    def save(self, **kwargs):
        try:
            blocked_user = User.objects.get(_id=ObjectId(self.validated_data['blocked_user']))
        except (User.DoesNotExist, bson_errors.InvalidId):
            raise serializers.ValidationError({"blocked_user": "Invalid user id"})

        user = kwargs.get('user')

        if user == blocked_user:
            raise serializers.ValidationError({"blocked_user": "You are not allowed to block yourself."})

        if Block.objects.filter(user=user, blocked_user=blocked_user).exists():
            raise serializers.ValidationError({"blocked_user": "You have already blocked this user."})

        # remove friendship requests
        friend_request = FriendRequest.objects.filter(initiator=user, receiver=blocked_user)
        mutual_friend_request = FriendRequest.objects.filter(initiator=blocked_user, receiver=user)

        if friend_request.exists():
            friend_request.delete()

        if mutual_friend_request.exists():
            mutual_friend_request.delete()

        super().save(blocked_user=blocked_user, **kwargs)


class PasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        try:
            user_payload = jwt.decode(attrs.get('token'), settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
        except (jwt.exceptions.InvalidSignatureError, jwt.ExpiredSignatureError, jwt.exceptions.DecodeError) as e:
            raise serializers.ValidationError('invalid password reset token provided')
        else:
            attrs['user_id'] = user_payload.get('user_id')
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('confirm password must be the same as new password')
        return attrs

