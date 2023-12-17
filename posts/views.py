from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from posts.models import Post, Like, Comment
from posts.serializers import PostSerializer, PostDetailSerializer, CommentSerializer

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from bson import ObjectId
from rest_framework.response import Response
from rest_framework import status


class PostView(ListCreateAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostDetailSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_object(self):
        _id = self.kwargs['_id']
        return Post.objects.get(_id=ObjectId(_id))


class PostLikeView(RetrieveUpdateDestroyAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_object(self):
        _id = self.kwargs['_id']
        return Post.objects.get(_id=ObjectId(_id))

    def perform_update(self, serializer):
        user = self.request.user
        post = self.get_object()

        liked = post.likes.filter(author=user)
        if liked:
            post.likes.remove(liked[0])
        else:
            like = Like.objects.create(author=user, post=post)
            post.likes.add(like)

        post.save()


class CommentView(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = '_id'

    def get_queryset(self):
        _id = self.kwargs['_id']
        return Comment.objects.filter(post=ObjectId(_id))

    def perform_create(self, serializer):
        if serializer.is_valid(raise_exception=True):
            return serializer.save(author=self.request.user, post=Post.objects.get(_id=ObjectId(self.kwargs['_id'])))

    def create(self, request, *args, **kwargs):
        try:
            comment = self.perform_create(self.get_serializer(data=request.data))
            return Response(status=status.HTTP_201_CREATED, data=self.get_serializer(comment).data)

        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
