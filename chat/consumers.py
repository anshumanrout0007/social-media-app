import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_user = self.scope['url_route']['kwargs']['username']
        self.current_user = self.scope['user']
        
        # Create a consistent room name from both usernames
        users = sorted([self.current_user.username, self.room_user])
        self.room_name = f"chat_{'_'.join(users)}"
        
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return
        
        # Save message to DB
        message = await self.save_message(message_text)
        
        await self.channel_layer.group_send(
            self.room_name,
            {
                'type': 'chat_message',
                'message': message_text,
                'sender': self.current_user.username,
                'sender_pic': await self.get_profile_pic(),
                'timestamp': message.timestamp.strftime('%H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, content):
        receiver = User.objects.get(username=self.room_user)
        return Message.objects.create(
            sender=self.current_user,
            receiver=receiver,
            content=content
        )

    @database_sync_to_async
    def get_profile_pic(self):
        user = User.objects.get(username=self.current_user.username)
        return user.profile_pic.url if user.profile_pic else ''