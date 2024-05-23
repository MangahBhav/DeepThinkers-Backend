from djongo import models


class Chat(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    private = models.BooleanField(default=True)
    last_message = models.ForeignKey('chats.Message', null=True, on_delete=models.SET_NULL, related_name='latest_chat')
    date = models.DateTimeField(auto_now_add=True)
    initiator = models.ForeignKey('users.User', on_delete=models.CASCADE)


class Member(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    chat = models.ForeignKey('chats.Chat', on_delete=models.CASCADE, related_name='members')
    date = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    user = models.ForeignKey('users.User', related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    chat = models.ForeignKey('chats.Chat', on_delete=models.CASCADE, related_name='messages')
    date = models.DateTimeField(auto_now_add=True)