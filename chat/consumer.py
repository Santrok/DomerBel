import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from users.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user_id = text_data_json["userId"]
        await database_sync_to_async(Message.objects.create)(chat_id=self.room_name,
                                                             author_id=user_id,
                                                             message=message)

        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message",
                                   "message": message,
                                   "userId": user_id
                                   })

    async def chat_message(self, event):
        message = event["message"]
        user_id = event["userId"]
        await self.send(text_data=json.dumps({"message": message, "userId": user_id}))
