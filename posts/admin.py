from django.contrib import admin

from esoteric_minds.utils import BaseModelAdmin
from posts.models import Post, Comment


@admin.register(Post)
class PostModelAdmin(BaseModelAdmin):
    pass


@admin.register(Comment)
class CommentModelAdmin(BaseModelAdmin):
    pass
