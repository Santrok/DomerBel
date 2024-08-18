from django.urls import path, re_path
from .consumer import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path("" , ChatConsumer.as_asgi()) ,
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()) ,
]