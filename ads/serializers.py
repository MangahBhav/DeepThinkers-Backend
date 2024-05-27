from rest_framework import serializers
from ads.models import Advert


class AdvertSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Advert
        fields = "__all__"