from django.urls import path
from ads.views import AdvertListView


urlpatterns = [
    path('', AdvertListView.as_view(), name='adverts'),
]