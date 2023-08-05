from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/channels/(?P<channel_id>\w+)/$",
        consumers.ChannelConsumer.as_asgi(),
    ),
]
