import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class CommunityConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        
        # Extract room name from URL (e.g. category_123 or global)
        self.room_name = self.scope['url_route']['kwargs'].get('room_name', 'global')
        self.room_group_name = f"community_{self.room_name}"
        
        # Verify if user is authenticated
        if self.user is None or not self.user.is_authenticated:
            print(f"Warning: Anonymous user connecting to {self.room_group_name}")
        else:
            print(f"User {self.user.email} connecting to {self.room_group_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive_json(self, content):
        # Echo message back to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': content
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send_json(message)
