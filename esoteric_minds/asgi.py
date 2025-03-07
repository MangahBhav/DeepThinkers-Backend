"""
ASGI config for esoteric_minds project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'esoteric_minds.settings')
django.setup()

import posts.routing
import chats.routing
from .middleware import TokenAuthMiddleware



# application = get_asgi_application()
url_patterns = []

url_patterns.extend(posts.routing.websocket_urlpatterns)
url_patterns.extend(chats.routing.websocket_urlpatterns)

application = ProtocolTypeRouter({
  'http': get_asgi_application(),
  'websocket': TokenAuthMiddleware(URLRouter(
      url_patterns
  )),
})
