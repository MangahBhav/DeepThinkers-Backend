from rest_framework import serializers

from posts.models import Post, Comment
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['_id', 'title', 'content', 'date', 'user', 'anonymous', 'likes_count', 'comments_count']


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['_id', 'content', 'date', 'user', 'anonymous']


class PostDetailSerializer(PostSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = PostSerializer.Meta.fields + ['comments']
