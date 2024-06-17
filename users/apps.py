from django.apps import AppConfig
from django.conf import settings


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from esoteric_minds import scheduler
        if settings.SCHEDULER_AUTOSTART:
            scheduler.start()
