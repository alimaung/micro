from django.urls import re_path
from microapp.consumers import RelayConsumer

websocket_urlpatterns = [
    re_path(r'ws/relay/$', RelayConsumer.as_asgi()),
]