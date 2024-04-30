from django.urls import path

from posts.views import PostView
from users.views import RegisterView, LoginView, UserDetailView, UserSearchView, FriendRequestView, BlockUserView

urlpatterns = [
    path('', UserSearchView.as_view(), name='users'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('blocks/', BlockUserView.as_view(), name="block-user"),
    path('<str:_id>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:user_id>/posts/', PostView.as_view(), name='user_posts'),
    path('<str:_id>/friends/', FriendRequestView.as_view(), name='user_friend_request_view')
]
