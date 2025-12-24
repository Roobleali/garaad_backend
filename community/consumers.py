import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class CommunityConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        
        # Verify if user is authenticated
        if self.user is None or not self.user.is_authenticated:
             # Option 1: Reject connection
             # await self.close()
             # return
             
             # Option 2: Accept but log (current behavior asked by user previously?)
             print("Warning: Anonymous user connected")
        else:
            print(f"User connected: {self.user.email}")

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
