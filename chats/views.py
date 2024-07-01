from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from chats.models import Chat, Member
from chats.serializers import ChatSerializer, MessageSerializer
from users.models import User
from bson import ObjectId
from django.db.models import Q


class CreateMessageView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def perform_create(self, serializer: MessageSerializer):
        try:
            receiver = User.objects.get(_id=ObjectId(serializer.validated_data.pop('receiver')))
        except User.DoesNotExist:
            raise ValidationError(detail={"receiver": "This user has been deleted or does not exist"})
        
        chat = Chat.objects.filter(Q(members__user=self.request.user) & Q(members__user=receiver))

        if chat.exists():
            return serializer.save(chat=chat[0], user=self.request.user)

        chat = Chat.objects.create(initiator=self.request.user)

        Member.objects.create(user=self.request.user, chat=chat)
        Member.objects.create(user=receiver, chat=chat)

        serializer.save(chat=chat, user=self.request.user)
    

class ListMessagesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer

    def get_queryset(self):
        return Chat.objects.filter(members__user=self.request.user)

