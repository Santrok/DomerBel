import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import UserMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Присоединение к группе чата
        """
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """
        Отключение от группы чата
        """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Отправка сообщения всем участникам комнаты
        """
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get("message")
            user_id = text_data_json.get("userId")
            timestamp = text_data_json.get("time")

            if message is None or user_id is None or timestamp is None:
                raise ValueError("Missing required fields in message")

            await database_sync_to_async(UserMessage.objects.create)(chat_id=self.room_name,
                                                                     author_id=user_id,
                                                                     message=message
                                                                     )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat.message",
                    "message": message,
                    "userId": user_id,
                    "time": timestamp,
                }
            )
        except Exception as e:
            #  логирование
            print(f"Error processing message: {str(e)}")

    async def chat_message(self, event):
        """
        Отправка сообщения обратно клиенту
        """
        message = event["message"]
        user_id = event["userId"]
        time = event["time"]

        await self.send(text_data=json.dumps({"message": message,
                                              "userId": user_id,
                                              "time": time
                                              }))
