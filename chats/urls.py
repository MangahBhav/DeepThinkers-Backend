from django.urls import path
from chats.views import CreateMessageView, ListMessagesView


urlpatterns = [
    path('', CreateMessageView.as_view(), name='create_message'),
    path('chats/', ListMessagesView.as_view(), name='list_messages')
]
