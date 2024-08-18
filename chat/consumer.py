import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from advertisement.models import Advertisement
from users.models import Chat, User, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.roomGroupName = "group_chat_gfg"
        await self.channel_layer.group_add(
            self.roomGroupName ,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self , close_code):
        await self.channel_layer.group_discard(
            self.roomGroupName ,
            self.channel_layer
        )
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = text_data_json["username"]
        user_id = text_data_json["userId"]
        advertisement = await sync_to_async(get_object_or_404)(Advertisement, id=text_data_json['advertisement'])
        users = await sync_to_async(User.objects.filter)(id__in=[advertisement.author_id, user_id])
        query = Chat.objects.filter(advertisement_id=advertisement.id, members__in=users)
        chat = await sync_to_async(list)(query)
        if chat:
            await sync_to_async(Message.objects.create)(chat=chat[0],
                                                        author_id=user_id,
                                                        message=message)

        else:
            chat = await sync_to_async(Chat.objects.create)(advertisement_id=advertisement.id)
            await sync_to_async(chat.members.set)(users)
            await sync_to_async(Message.objects.create)(chat=chat,
                                                        author_id=user_id,
                                                        message=message)

        await self.channel_layer.group_send(
            self.roomGroupName,{
                "type" : "sendMessage" ,
                "message" : message ,
                "username" : username ,
            })
    async def sendMessage(self , event) :
        message = event["message"]
        username = event["username"]
        await self.send(text_data = json.dumps({"message":message ,"username":username}))