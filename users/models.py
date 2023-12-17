import datetime

from djongo import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

from esoteric_minds import settings
import jwt


class User(AbstractUser, models.Model):
    _id = models.ObjectIdField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profile_image = CloudinaryField('profile_image', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def create_auth_token(self):
        user_token_payload = {
            "user_id": str(self._id),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=720),
            "iat": datetime.datetime.utcnow()
        }
        token = jwt.encode(user_token_payload, settings.SECRET_KEY, settings.JWT_ENCRYPTION_METHOD)
        return token

    def save(self, *args, **kwargs):
        self.set_password(self.password)
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username
