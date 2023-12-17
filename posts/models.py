from djongo import models
# Create your models here.


class Post(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    anonymous = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def user(self):
        if self.anonymous:
            return None
        return self.author

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()

    def __str__(self):
        return self.title


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


class Like(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name='likes')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, related_name='likes')
    author = models.ForeignKey('users.User', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.author