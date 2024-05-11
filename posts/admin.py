from django.contrib import admin

from esoteric_minds.utils import BaseModelAdmin
from posts.models import Post, Comment, Topic


@admin.register(Post)
class PostModelAdmin(BaseModelAdmin):
    search_fields = ['content', 'author__username', 'author__email']


@admin.register(Comment)
class CommentModelAdmin(BaseModelAdmin):
    pass


@admin.register(Topic)
class TopicModelAdmin(BaseModelAdmin):
    pass
