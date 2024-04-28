from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from posts.models import Post, Like, Comment
from posts.serializers import PostSerializer, PostDetailSerializer, CommentSerializer, LikeSerializer

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bson import ObjectId, errors as bson_errors
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404


class PostView(ListCreateAPIView):
    serializer_class = PostSerializer
    # queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.kwargs.get('user_id'):
            return Post.objects.filter(author=ObjectId(self.kwargs['user_id']))
        return Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def check_object_permissions(self, request, obj):
        safe_methods = ('GET', 'HEAD', 'OPTIONS')
        super().check_object_permissions(request, obj)

        if request.method in safe_methods:
            return

        if request.user._id != obj.author._id:
            self.permission_denied(request, message='You do not have permission to perform this action.')

    def perform_update(self):
        serializer = self.get_serializer(instance=self.get_object(), data=self.request.data, partial=True)

        self.check_object_permissions(self.request, self.get_object())
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        self.check_object_permissions(request, self.get_object())
        return self.perform_update()

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, instance)
        instance.delete()

    def get_object(self):
        try:
            _id = self.kwargs['_id']
            return Post.objects.get(_id=ObjectId(_id))
        except Post.DoesNotExist:
            raise Http404("post does not exist")


class PostLikeView(RetrieveUpdateDestroyAPIView):
    serializer_class = LikeSerializer
    queryset = Like.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_post(self):
        _id = self.kwargs['_id']
        return Post.objects.get(_id=ObjectId(_id))

    def get_object(self):
        try:
            return Like.objects.get(user=self.request.user, post=self.get_post())
        except Like.DoesNotExist:
            return None

    # def get_serializer(self, *args, **kwargs):
    #     return self.serializer_class(instance=self.get_object())

    def perform_update(self, serializer):
        user = self.request.user
        post = self.get_post()

        liked = self.get_object()
        if liked and liked.category == self.request.data.get('category'):
            liked.delete()
        else:
            # like = Like.objects.create(author=user, post=post)
            serializer.save(user=user, post=post, category=self.request.data.get('category'))
            # post.likes.add(like)


class CommentView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_queryset(self):
        _id = self.kwargs.get('_id')
        return Comment.objects.filter(post=ObjectId(_id))

    def perform_create(self, serializer):
        try:
            if serializer.is_valid(raise_exception=True):
                return serializer.save(author=self.request.user, post=Post.objects.get(_id=ObjectId(self.kwargs['_id'])))
        except (Post.DoesNotExist, bson_errors.InvalidId):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            comment = self.perform_create(self.get_serializer(data=request.data))
            return Response(status=status.HTTP_201_CREATED, data=self.get_serializer(comment).data)

        except (Post.DoesNotExist, bson_errors.InvalidId):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        try:
            response = super().list(request, *args, **kwargs)
            response.data['post'] = PostSerializer(instance=Post.objects.get(_id=ObjectId(self.kwargs['_id']))).data
            return response

        except (Post.DoesNotExist, bson_errors.InvalidId):
            return Response(status=status.HTTP_404_NOT_FOUND)


class CommentDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_object(self):
        try:
            return Comment.objects.get(_id=ObjectId(self.kwargs['_id']))
        except Comment.DoesNotExist:
            raise Http404("comment does not exist")

    def check_object_permissions(self, request, obj):
        if request and request.user.is_authenticated:
            if request.user._id != obj.author._id:
                self.permission_denied(request, message='You do not have permission to perform this action.')
        return super().check_object_permissions(request, obj)

    def perform_destroy(self, instance):
        self.check_object_permissions(self.request, instance)
        instance.delete()
