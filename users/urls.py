from django.urls import path

from posts.views import PostView
from users.views import RegisterView, LoginView, UserDetailView, UserSearchView, FriendRequestView, BlockUserView, UserPasswordResetRequest, PasswordResetView

urlpatterns = [
    path('', UserSearchView.as_view(), name='users'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('request-password-reset/', UserPasswordResetRequest.as_view(), name='request_password_reset'),
    path('reset-password/', PasswordResetView.as_view(), name='reset_password'),
    path('blocks/', BlockUserView.as_view(), name="block-user"),
    path('<str:_id>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:user_id>/posts/', PostView.as_view(), name='user_posts'),
    path('<str:_id>/friends/', FriendRequestView.as_view(), name='user_friend_request_view'),
]
