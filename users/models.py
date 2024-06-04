import datetime

from djongo import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

from django.conf import settings
import jwt


class User(AbstractUser, models.Model):
    _id = models.ObjectIdField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image = CloudinaryField('profile_image', folder='esoteric-minds', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    city = models.CharField(max_length=200, null=True)
    country = models.CharField(max_length=200, default="")
    state = models.CharField(max_length=200, null=True)

    # blocked_users = models.ArrayReferenceField('users.User', on_delete=models.CASCADE)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def create_auth_token(self):
        user_token_payload = {
            "user_id": str(self._id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(user_token_payload, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
        return token

    def has_added_friend(self, friend):
        return self.initiated_friend_requests.filter(receiver=friend).exists()

    def has_blocked_user(self, user):
        return self.user_blocks.filter(blocked_user=user).exists()

    def is_member(self, topic):
        return self.joined_topics.filter(topic=topic).exists()

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username


class FriendRequest(models.Model):
    initiator = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                  related_name='initiated_friend_requests')
    receiver = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                 related_name='received_friend_requests')
    mutual = models.BooleanField(default=False)


class Block(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                             related_name='user_blocks')
    blocked_user = models.ForeignKey('users.User', on_delete=models.CASCADE,
                                     related_name='blocked_by_others')
