from rest_framework import serializers

from posts.models import Post, Comment, Like, FlagPost, Topic, TopicMember
from users.models import User
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


class PostUserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required=False)
    added_friend = serializers.BooleanField(default=True, initial=True)
    blocked_user = serializers.BooleanField(default=False, initial=False)

    def get_added_friend(self, obj):
        return True

    def get_blocked_user(self, obj):
        return False

    class Meta:
        model = User
        fields = ['_id', 'username', 'email', 'profile_image', 
                  'blocked_user', 'added_friend', 'date', 'city', 'state', 'country', 'star', 'is_staff']


class PostSerializer(serializers.ModelSerializer):
    user = PostUserSerializer(read_only=True)

    liked = serializers.SerializerMethodField()
    flagged = serializers.BooleanField(default=False, read_only=True)

    def get_liked(self, post):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else self.context.get('user')
        if user:
            liked = post.get_liked(self.context.get('user') or request.user)
            if liked:
                return liked.category
        return None

    # def get_flagged(self, post):
    #     request = self.context.get('request')
    #     user = request.user if request and request.user.is_authenticated else self.context.get('user')
    #     if user:
    #         flagged = post.get_flagged(self.context.get('user') or request.user)
    #         return flagged
    #     return False

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

        user = kwargs.get('user')
        if FlagPost.objects.filter(user=user, post=post).exists():
            raise serializers.ValidationError({"post": "Post already flagged"})

        super().save(post=post, **kwargs)

    class Meta:
        model = FlagPost
        fields = "__all__"


class ListFlagPostSerializer(serializers.ModelSerializer):
    user = serializers.CharField()
    post = PostSerializer()

    class Meta:
        model = FlagPost
        fields = "__all__"


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class TopicMemberSerializer(serializers.ModelSerializer):
    topic = serializers.CharField(required=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = TopicMember
        fields = "__all__"
