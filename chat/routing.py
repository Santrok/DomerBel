from django.urls import path, re_path
from .consumer import ChatConsumer

# Here, "" is routing to the URL ChatConsumer which
# will handle the chat functionality.
websocket_urlpatterns = [
    path("" , ChatConsumer.as_asgi()) ,
    path(r"ws/chat/<str:room_name>/", ChatConsumer.as_asgi()) ,
]