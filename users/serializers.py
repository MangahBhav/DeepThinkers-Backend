from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User, FriendRequest, Block
from bson import ObjectId, errors as bson_errors


class UserSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(read_only=True)
    profile_image = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    added_friend = serializers.SerializerMethodField()
    blocked_user = serializers.SerializerMethodField()

    def get_added_friend(self, user):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.added_friend(user)
        return False

    def get_blocked_user(self, user):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.blocked_user(user)
        return False

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ['_id', 'username', 'email', 'profile_image', 'added_friend', 'blocked_user', 'password', 'date']


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

        super().save(blocked_user=blocked_user, **kwargs)
