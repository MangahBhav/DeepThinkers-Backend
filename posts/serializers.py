from rest_framework import serializers

from posts.models import Post, Comment, Like
from users.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['_id', 'title', 'content', 'date', 'user', 'anonymous', 'likes_count', 'comments_count',
                  'likes_details']


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


class LikeSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=(('very_deep', 'very_deep'), ('deep', 'deep'),
                                                ('shallow', 'shallow'), ('very_shallow', 'very_shallow')),
                                       required=True, allow_blank=False)
    post = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Like
        fields = "__all__"
