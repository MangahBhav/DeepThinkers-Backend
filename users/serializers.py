from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    _id = serializers.CharField(read_only=True)
    profile_image = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['_id', 'username', 'email', 'profile_image', 'password', 'date']


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
