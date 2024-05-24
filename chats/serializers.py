from rest_framework import serializers

from chats.models import Chat, Member, Message
from users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    receiver = serializers.CharField(write_only=True, required=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["_id", "content", "date", "user", "receiver"]


class MemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Member
        fields = ['user']


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(read_only=True, many=True)
    members = MemberSerializer(read_only=True, many=True)

    class Meta:
        model = Chat
        fields = ["messages", "members"]

