from djongo import models
from cloudinary.models import CloudinaryField


class Advert(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    image = CloudinaryField('ad_image', folder='esoteric-minds', null=False)
    content = models.TextField(null=False)
    redirect_link = models.URLField(null=False)