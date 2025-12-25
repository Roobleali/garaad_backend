from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Match ws/community/ or ws/community/<room_name>/
    re_path(r'ws/community/(?P<room_name>[^/]+)/?$', consumers.CommunityConsumer.as_asgi()),
    re_path(r'ws/community/?$', consumers.CommunityConsumer.as_asgi()),
]
