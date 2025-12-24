from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Match ws/community/ with any query parameters
    re_path(r'ws/community/?$', consumers.CommunityConsumer.as_asgi()),
]
