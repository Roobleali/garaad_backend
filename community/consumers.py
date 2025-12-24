import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class CommunityConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # In a real app, we would verify the token here.
        # For now, we accept the connection to resolve the connection error.
        self.room_group_name = "community_global"

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
