from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from users.models import User
from users.serializers import UserSerializer, LoginSerializer
from bson import ObjectId

from django.http import Http404

class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []


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
        serializer = self.get_serializer(instance=self.get_object(), data=self.request.data, partial=True)

        self.check_object_permissions(self.request, self.get_object())
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        return self.perform_update(self.get_serializer())

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, self.get_object())
        instance.delete()