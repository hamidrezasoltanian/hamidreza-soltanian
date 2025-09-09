import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Notification
from .serializers import NotificationSerializer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"user_{self.user.id}"
        self.room_group_name = f"notifications_{self.room_name}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send unread notifications count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'mark_as_read':
            notification_id = text_data_json.get('notification_id')
            await self.mark_notification_as_read(notification_id)
        elif message_type == 'mark_all_as_read':
            await self.mark_all_as_read()
        elif message_type == 'get_notifications':
            page = text_data_json.get('page', 1)
            notifications = await self.get_notifications(page)
            await self.send(text_data=json.dumps({
                'type': 'notifications_list',
                'notifications': notifications
            }))
    
    # Receive message from room group
    async def notification_message(self, event):
        notification = event['notification']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': notification
        }))
        
        # Update unread count
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
    
    @database_sync_to_async
    def get_notifications(self, page=1):
        notifications = Notification.objects.filter(
            user=self.user
        ).order_by('-created_at')[:20]
        
        serializer = NotificationSerializer(notifications, many=True)
        return serializer.data
    
    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.user
            )
            notification.is_read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False
    
    @database_sync_to_async
    def mark_all_as_read(self):
        Notification.objects.filter(
            user=self.user,
            is_read=False
        ).update(is_read=True)


class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.room_name = f"dashboard_{self.user.id}"
        self.room_group_name = f"dashboard_{self.room_name}"
        
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
    
    # Receive message from room group
    async def dashboard_update(self, event):
        update_type = event['type']
        data = event['data']
        
        # Send update to WebSocket
        await self.send(text_data=json.dumps({
            'type': update_type,
            'data': data
        }))
    
    # Handle different types of dashboard updates
    async def customer_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'customer_update',
            'data': event['data']
        }))
    
    async def invoice_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'invoice_update',
            'data': event['data']
        }))
    
    async def product_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'product_update',
            'data': event['data']
        }))