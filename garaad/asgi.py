import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from community.middleware import JwtAuthMiddleware
from channels.security.websocket import OriginValidator
from django.conf import settings
import community.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'garaad.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": OriginValidator(
        JwtAuthMiddleware(
            URLRouter(
                community.routing.websocket_urlpatterns
            )
        ),
        settings.CORS_ALLOWED_ORIGINS
    ),
})
