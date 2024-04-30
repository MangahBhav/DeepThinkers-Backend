from rest_framework import serializers

from posts.models import Post, Comment, Like, FlagPost
from users.serializers import UserSerializer

from bson import ObjectId, errors as bson_errors


class LikeSerializer(serializers.ModelSerializer):
    category = serializers.ChoiceField(choices=(('very_deep', 'very_deep'), ('deep', 'deep'),
                                                ('shallow', 'shallow'), ('very_shallow', 'very_shallow')),
                                       required=True, allow_blank=False)
    post = serializers.CharField(read_only=True)
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Like
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    liked = serializers.SerializerMethodField()
    flagged = serializers.SerializerMethodField()

    def get_liked(self, post):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            liked = post.get_liked(request.user)
            if liked:
                return liked.category
        return None

    def get_flagged(self, post):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            flagged = post.get_flagged(request.user)
            return flagged
        return False

    class Meta:
        model = Post
        fields = ['_id', 'title', 'content', 'date', 'user', 'anonymous', 'comments_count',
                  'likes_details', 'liked', 'flagged']


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


class FlagPostSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    post = serializers.CharField()

    def save(self, **kwargs):
        try:
            post = Post.objects.get(_id=ObjectId(self.validated_data['post']))
        except (Post.DoesNotExist, bson_errors.InvalidId):
            raise serializers.ValidationError({"post": "Invalid post id"})

        super().save(post=post, **kwargs)

    class Meta:
        model = FlagPost
        fields = "__all__"
