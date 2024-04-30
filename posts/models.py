from djongo import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

# Create your models here.


class Post(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    topic = models.ForeignKey('posts.Topic', on_delete=models.CASCADE, null=True)
    anonymous = models.BooleanField(default=False)
    very_deep = models.IntegerField(default=0)
    deep = models.IntegerField(default=0)
    shallow = models.IntegerField(default=0)
    very_shallow = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def user(self):
        if self.anonymous:
            return None
        return self.author

    @property
    def likes_details(self):

        return {
            "very_deep": self.very_deep or 0,
            "deep": self.deep or 0,
            "shallow": self.shallow or 0,
            "very_shallow": self.very_shallow or 0
        }

    def get_liked(self, user):
        return self.likes.filter(user=user).first()

    def get_flagged(self, user):
        return FlagPost.objects.filter(post=self, user=user).exists()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-_id']


class Comment(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def user(self):
        if self.anonymous:
            return None
        return self.author

    def __str__(self):
        return self.content

    class Meta:
        ordering = ['-_id']


class Like(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name='likes')
    # comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name='likes')
    category = models.CharField(choices=(('very_deep', 'very_deep'), ('deep', 'deep'),
                                         ('shallow', 'shallow'), ('very_shallow', 'very_shallow')), max_length=20,
                                null=False, blank=False)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.category


class Topic(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Like)
def update_post_likes(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        setattr(post, instance.category, (getattr(post, instance.category) or 0) + 1)
        post.save()


@receiver(post_delete, sender=Like)
def update_post_likes_on_delete(sender, instance, **kwargs):
    post = instance.post
    setattr(post, instance.category, (getattr(post, instance.category) or 1) - 1)
    post.save()


@receiver(post_save, sender=Comment)
def update_comment_count(sender, instance, created, **kwargs):
    if created:
        post = instance.post
        post.comments_count = post.comments_count or 0
        post.comments_count += 1
        post.save()


@receiver(post_delete, sender=Comment)
def update_comment_count_on_delete(sender, instance, **kwargs):
    post = instance.post
    post.comments_count = post.comments_count or 1
    post.comments_count -= 1
    post.save()


class FlagPost(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    post = models.ForeignKey('posts.Post', on_delete=models.CASCADE)
