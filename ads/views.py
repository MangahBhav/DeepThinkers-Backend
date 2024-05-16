from rest_framework.generics import ListAPIView
from ads.serializers import AdvertSerializer
from ads.models import Advert


class AdvertListView(ListAPIView):
    serializer_class = AdvertSerializer
    queryset = Advert.objects.all()
