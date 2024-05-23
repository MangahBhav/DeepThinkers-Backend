from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from chats.models import Chat, Member
from chats.serializers import MessageSerializer
from users.models import User
from bson import ObjectId


class CreateMessageView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def perform_create(self, serializer: MessageSerializer):
        print(serializer)
        receiver = User.objects.get(_id=ObjectId(serializer.validated_data.pop('receiver')))

        chat = Chat.objects.filter(members__user__in=[self.request.user, receiver])

        print(chat)

        if chat.exists():
            # chat.last_message = 
            serializer.save(chat=chat[0], user=self.request.user)
            return

        chat = Chat.objects.create(initiator=self.request.user)

        Member.objects.create(user=self.request.user, chat=chat)
        Member.objects.create(user=receiver, chat=chat)

        serializer.save(chat=chat, user=self.request.user)
        # chat.save()
        
        # return super().perform_create(serializer)
    

class ListMessagesView(ListAPIView):
    pass