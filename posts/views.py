from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView, \
    DestroyAPIView

from posts.models import Post, Like, Comment, Topic, TopicMember, FlagPost
from posts.serializers import PostSerializer, PostDetailSerializer, CommentSerializer, LikeSerializer, \
    FlagPostSerializer, TopicSerializer, TopicMemberSerializer, ListFlagPostSerializer

from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from bson import ObjectId, errors as bson_errors
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404, HttpResponseBadRequest
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from djongo.models import Q

from django.core.cache import cache


class PostView(ListCreateAPIView):
    serializer_class = PostSerializer
    # queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.kwargs.get('user_id'):
            return Post.objects.filter(author=ObjectId(self.kwargs['user_id'])).select_related('author')

        if self.kwargs.get('topic_id'):
            return Post.objects.filter(topic=ObjectId(self.kwargs['topic_id'])).select_related('author')
        
        if self.request.user.is_authenticated:
            return Post.objects.prefetch_related('likes').exclude(
                Q(author__in=list(map(lambda x: x.blocked_user, self.request.user.user_blocks.all()))) |
                Q(_id__in=list(map(lambda x: x.post._id, self.request.user.flagged_posts.all())))
            )
        return Post.objects.filter(topic=None).select_related('author')

    def perform_create(self, serializer):
        topic = self.kwargs.get('topic_id')
        # check if user is a member
        if topic:
            try:
                topic = Topic.objects.get(_id=ObjectId(topic))

            except (Topic.DoesNotExist, bson_errors.InvalidId):
                raise Http404("topic not found")

        if topic and not self.request.user.is_member(topic):
            raise PermissionDenied("user is not a member of this topic")
        serializer.save(author=self.request.user, topic=topic if topic else None)

    # @method_decorator(cache_page(60 * 120))  # Cache the view for 2 hours
    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        if self.kwargs.get('user_id') or self.kwargs.get('topic_id'):
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                return response

            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
            return response

        cache_key = f"feed_{str(self.request.user._id)}" if self.request.user.is_authenticated else "feed"
        data = cache.get(cache_key)

        if not data:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                response = self.get_paginated_response(serializer.data)
                cache.set(cache_key, response.data, 60 * 120)
                return response

            serializer = self.get_serializer(queryset, many=True)
            response = Response(serializer.data)
            cache.set(cache_key, response.data, 60 * 120)
            return response
        
        return Response(data=data)

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
        liked = Like.objects.filter(user=self.request.user, post=self.get_post())
        if liked.exists():
            return Like.objects.filter(user=self.request.user, post=self.get_post())[0]
        return None

    # def get_serializer(self, *args, **kwargs):
    #     return self.serializer_class(instance=self.get_object())

    def perform_update(self, serializer):
        user = self.request.user
        post = self.get_post()

        liked = self.get_object()
        if liked:
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


SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class FlagPostView(ListCreateAPIView, DestroyAPIView):
    # serializer_class = FlagPostSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return FlagPostSerializer
        else:
            return ListFlagPostSerializer

    def get_queryset(self):
        return FlagPost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        try:
            post = Post.objects.get(_id=ObjectId(self.request.data.get('post')))
        except (Post.DoesNotExist, bson_errors.InvalidId):
            raise ValidationError({"post": "Invalid post id"})

        flagged_post_queryset = queryset.filter(user=self.request.user, post=post)
        if flagged_post_queryset.exists():
            return flagged_post_queryset[0]
        return None

    def perform_destroy(self, instance):
        if not instance:
            raise ValidationError({"post": "you have not flagged this post."})
        instance.delete()


class TopicListView(ListAPIView):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = [IsAuthenticated]


class TopicMemberView(ListCreateAPIView):
    serializer_class = TopicMemberSerializer
    queryset = TopicMember.objects.all()
    permission_classes = [IsAuthenticated]

    # def get_serializer(self, *args, **kwargs):
    #     try:
    #         topic = Topic.objects.get(_id=ObjectId(self.kwargs.get('topic_id')))
    #
    #         if self.request.user.is_member(topic):
    #             member = TopicMember.objects.filter(topic=topic, user=self.request.user)[0]
    #             return self.serializer_class(instance=member, data=self.request.data)
    #
    #         return super().get_serializer(*args, **kwargs)
    #
    #     except (Topic.DoesNotExist, bson_errors.InvalidId):
    #         print(self.kwargs.get('topic_id'))
    #         raise Http404("topic not found")

    def perform_create(self, serializer):
        try:
            topic = Topic.objects.get(_id=ObjectId(self.kwargs.get('topic_id')))
            if self.request.user.is_member(topic):
                raise PermissionDenied("you have already joined this topic.")

            serializer.save(user=self.request.user, topic=topic)

        except (Topic.DoesNotExist, bson_errors.InvalidId):
            print(self.kwargs.get('topic_id'))
            raise Http404("topic not found")
