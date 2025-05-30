from django.urls import re_path
from microapp.consumers import RelayConsumer, SMAConsumer, SMAFilmingConsumer

websocket_urlpatterns = [
    re_path(r'ws/relay/$', RelayConsumer.as_asgi()),
    re_path(r'ws/sma/$', SMAConsumer.as_asgi()),
    re_path(r'ws/sma/(?P<session_id>\w+)/$', SMAFilmingConsumer.as_asgi()),
]