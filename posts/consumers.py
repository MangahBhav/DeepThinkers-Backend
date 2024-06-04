from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json
from .models import Post
from .serializers import PostSerializer
from bson import ObjectId


class PostFeedConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room_name = None
        self.room_group_name = None
        self.room = None

    def connect(self):
        self.room_name = 'feed'
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)

        if data['type'] == 'post_feed':
            # TODO: get post data from database
            # Feed post data to the client
            post = Post.objects.get(_id=ObjectId(data['post']))
            data = {
                "post": PostSerializer(instance=post, context={"user": self.scope['user']}).data
            }

            async_to_sync(self.channel_layer.group_send)(
                self.room_name,
                {
                    'type': 'post_feed',
                    'message': data,
                }
            )

    def post_feed(self, event):
        print('from post feed method?', event)
        self.send(text_data=json.dumps(event))
