from django.contrib import admin

from esoteric_minds.utils import BaseModelAdmin
from users.models import User


@admin.register(User)
class UserModelAdmin(BaseModelAdmin):
    pass


