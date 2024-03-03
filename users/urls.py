from django.urls import path
from users.views import RegisterView, LoginView, UserDetailView, UserSearchView, FriendRequestView

urlpatterns = [
    path('', UserSearchView.as_view(), name='users'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('<str:_id>/', UserDetailView.as_view(), name='user-detail'),
    path('<str:_id>/friends/', FriendRequestView.as_view(), name='user_friend_request_view')
]
