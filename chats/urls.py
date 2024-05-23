from django.urls import path
from chats.views import CreateMessageView


urlpatterns = [
    path('', CreateMessageView.as_view(), name='create_message'),
]
