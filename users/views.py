import datetime

from rest_framework.generics import (CreateAPIView, RetrieveUpdateDestroyAPIView,
                                     ListAPIView, ListCreateAPIView, DestroyAPIView)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import ValidationError

from esoteric_minds import settings
from users.models import User, FriendRequest, Block
from users.serializers import UserSerializer, LoginSerializer, FriendRequestSerializer, BlockUserSerializer, \
    PasswordResetSerializer
from bson import ObjectId, errors as bson_errors
from rest_framework import filters
from django.http import Http404
from django.core.mail import send_mail
import jwt


class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid(raise_exception=True):
            if request.ipinfo:
                if not request.ipinfo.all.get('bogon'):
                    serializer.validated_data['city'] = request.ipinfo.all.get('city', '')
                    serializer.validated_data['state'] = request.ipinfo.all.get('region', '')
                    serializer.validated_data['country'] = f"{request.ipinfo.all.get('country_name', '')}"
            user = serializer.create(serializer.validated_data)
            return Response(data=self.serializer_class(user).data, status=201)


class LoginView(CreateAPIView):
    serializer_class = LoginSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        user_serializer = UserSerializer(user)

        return Response({
            'user': user_serializer.data,
            'token': user.create_auth_token()
        })


class UserDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_object(self):
        try:
            _id = self.kwargs['_id']
            return User.objects.get(_id=ObjectId(_id))
        except User.DoesNotExist:
            raise Http404("user does not exist")

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        if request.method == 'GET':
            return

        if request.user._id != obj._id:
            self.permission_denied(request, message='You do not have permission to perform this action.')

    def perform_update(self, serializer):
        self.check_object_permissions(self.request, self.get_object())
        if serializer.is_valid(raise_exception=True):
            return serializer.save()

    def put(self, request, *args, **kwargs):
        user = self.perform_update(self.get_serializer(instance=self.get_object(),
                                                       data=self.request.data, partial=True))
        return Response(data=self.serializer_class(instance=user).data)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, self.get_object())
        instance.delete()


class UserSearchView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_queryset(self):
        return User.objects.all()


class FriendRequestView(ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        else:
            return FriendRequestSerializer

    def get_queryset(self):
        user_id = self.kwargs['_id']
        # retrieve all users that the user_id has made a friend request to.
        requests = FriendRequest.objects.filter(initiator=ObjectId(user_id))
        return User.objects.filter(_id__in=list(map(lambda x: x.receiver._id, requests)))

    def perform_create(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        try:
            initiator = self.request.user
            receiver = User.objects.get(_id=ObjectId(serializer.validated_data['receiver']))

            if initiator == receiver:
                raise ValidationError(detail="can not add yourself as a friend")

            friend_request = FriendRequest.objects.get_or_create(
                initiator=initiator,
                receiver=receiver
            )

            mutual_friend_request = FriendRequest.objects.get(
                initiator=receiver,
                receiver=initiator
            )

            if mutual_friend_request:
                friend_request.mutual = True
                mutual_friend_request.mutual = True

                friend_request.save()
                mutual_friend_request.save()

        except User.DoesNotExist:
            raise ValidationError(detail="user does not exist")

        except FriendRequest.DoesNotExist:
            pass


class BlockUserView(CreateAPIView, DestroyAPIView):
    serializer_class = BlockUserSerializer
    queryset = Block.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            blocked_user = User.objects.get(_id=ObjectId(self.request.data.get('blocked_user')))
        except (User.DoesNotExist, bson_errors.InvalidId):
            raise ValidationError({"blocked_user": "Invalid user id"})

        blocked_user_queryset = queryset.filter(user=self.request.user, blocked_user=blocked_user)
        if blocked_user_queryset.exists():
            return blocked_user_queryset[0]
        return None

    def perform_destroy(self, instance):
        if not instance:
            raise ValidationError({"blocked_user": "you have not blocked this user."})
        instance.delete()


class UserPasswordResetRequest(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').strip()
        user = User.objects.filter(email=email).first()

        if user:
            user_token_payload = {
                "user_id": str(user._id),
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10),
                "iat": datetime.datetime.utcnow()
            }
            token = jwt.encode(user_token_payload, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
            reset_link = f"https://esotericmynds.com/password-reset/{token}"
            subject = 'Password Reset [Esoteric Minds]'
            message = f"""
                            <p>Hi {user.first_name.title()},

                            There was a request to change your password!

                            If you did not make this request then please ignore this email.

                            Otherwise, please click this link to change your password: [<a href="{reset_link}">link</a>]
                            </p>
                       """
            send_mail(subject, '', settings.DEFAULT_FROM_EMAIL,
                      [user.email], html_message=message)
            return Response({'success': True, 'message': f'successfully sent password reset to {user.email}'})
        else:
            return Response({'success': False, 'message': 'user with this email does not exist'}, status=400)


class PasswordResetView(APIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        password_reset_serializer = self.serializer_class(data=request.data)
        if password_reset_serializer.is_valid(raise_exception=True):
            user_id = password_reset_serializer.validated_data['user_id']
            user = User.objects.get(_id=ObjectId(user_id))
            user.set_password(password_reset_serializer.validated_data['new_password'])
            user.save()
            return Response({'success': True, 'message': 'successfully reset password'})
