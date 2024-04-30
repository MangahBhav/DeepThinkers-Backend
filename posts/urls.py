# add views from posts/views.py:
from django.urls import path

from posts.views import PostView, PostDetailView, PostLikeView, CommentView, FlagPostView

urlpatterns = [
    path('', PostView.as_view(), name='posts'),
    path('flags/', FlagPostView.as_view(), name="flag-post"),
    path('<str:_id>/', PostDetailView.as_view(), name='post-detail'),
    path('<str:_id>/comments/', CommentView.as_view(), name='comments'),
    # path('posts/<str:pk>/comments/<str:comment_pk>/',
    #      CommentDetailView.as_view(), name='comment-detail'),
    path('<str:_id>/likes/', PostLikeView.as_view(), name='likes'),
    # path('posts/<str:pk>/likes/<str:like_pk>/',
    #      LikeDetailView.as_view(), name='like-detail'),
    # path('posts/<str:pk>/comments/<str:comment_pk>/likes/',
    #      CommentLikeView.as_view(), name='comment-likes'),
    # path('posts/<str:pk>/comments/<str:comment_pk>/likes/<str:like_pk>/',
    #      CommentLikeDetailView.as_view(), name='comment-like-detail'),
]