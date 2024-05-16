from django.contrib import admin
from ads.models import Advert
from esoteric_minds.utils import BaseModelAdmin


@admin.register(Advert)
class AdvertModelAdmin(BaseModelAdmin):
    pass