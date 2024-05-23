from rest_framework import serializers

from chats.models import Chat, Message
from users.serializers import UserSerializer


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message

class MessageSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(write_only=True, required=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["_id", "content", "date", "user", "receiver"]