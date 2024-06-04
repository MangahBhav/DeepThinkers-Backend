from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from .models import Message, Member
from .serializers import MessageSerializer
from bson import ObjectId
from django.core.exceptions import PermissionDenied


class ChatFeedConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    def connect(self):
        user = self.scope['user']
        print(user)
        if not user:
            self.close("provide a valid authentication token.")
            return
        
        self.room_name = f'inbox_{str(user._id)}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        if self.scope['user']:
            async_to_sync(self.channel_layer.group_discard)(
                self.room_name,
                self.channel_name
            )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data['type'] == 'incoming_message':
            try:
                message = Message.objects.get(_id=ObjectId(data['message']))

                if message.user != self.scope['user']:
                    raise PermissionDenied("can not send message on behalf of another user")

                users = list(map(lambda m: m.user, Member.objects.filter(chat=message.chat)))

                data = {
                    "message": MessageSerializer(instance=message).data
                }

                for user in users:
                    async_to_sync(self.channel_layer.group_send)(
                        f'inbox_{str(user._id)}',
                        {
                            'type': 'incoming_message',
                            'message': data,
                        }
                    )

            except Message.DoesNotExist:
                return

    def incoming_message(self, event):
        self.send(text_data=json.dumps(event))
