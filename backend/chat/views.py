from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Prefetch
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import ChatRoom, ChatMessage, MessageReadStatus, ChatRoomMembership
from .serializers import (
    ChatRoomSerializer, ChatMessageSerializer, MessageReadStatusSerializer,
    ChatRoomMembershipSerializer, CreateChatRoomSerializer
)
from authentication.models import CustomUser
from common.models import Mention, Notification
import json

class ChatRoomViewSet(viewsets.ModelViewSet):
    """مدیریت اتاق‌های چت"""
    
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            memberships__user=user,
            memberships__is_active=True
        ).prefetch_related(
            'members',
            'messages__sender',
            'memberships__user'
        ).distinct()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateChatRoomSerializer
        return ChatRoomSerializer
    
    @action(detail=False, methods=['get'])
    def my_rooms(self, request):
        """اتاق‌های کاربر"""
        rooms = self.get_queryset()
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """اضافه کردن عضو به اتاق"""
        room = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # بررسی دسترسی
        if not self._has_room_permission(room, request.user, 'admin'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        membership, created = ChatRoomMembership.objects.get_or_create(
            room=room,
            user=user,
            defaults={'invited_by': request.user}
        )
        
        if created:
            # ارسال اعلان
            Notification.objects.create(
                user=user,
                notification_type='mention',
                title=f'به اتاق "{room.name}" دعوت شدید',
                message=f'{request.user.get_full_name()} شما را به اتاق چت دعوت کرد',
                content_object=room
            )
            
            return Response({'message': 'Member added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Member already exists'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """حذف عضو از اتاق"""
        room = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # بررسی دسترسی
        if not self._has_room_permission(room, request.user, 'admin'):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            membership = ChatRoomMembership.objects.get(room=room, user=user)
            membership.is_active = False
            membership.save()
            
            return Response({'message': 'Member removed successfully'}, status=status.HTTP_200_OK)
        except ChatRoomMembership.DoesNotExist:
            return Response({'error': 'Member not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """پیام‌های اتاق"""
        room = self.get_object()
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        messages = ChatMessage.objects.filter(
            room=room,
            is_deleted=False
        ).select_related('sender').prefetch_related('read_status__user')[:page_size * page]
        
        serializer = ChatMessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
    def _has_room_permission(self, room, user, required_role):
        """بررسی دسترسی کاربر در اتاق"""
        try:
            membership = ChatRoomMembership.objects.get(room=room, user=user, is_active=True)
            role_hierarchy = {'admin': 4, 'moderator': 3, 'member': 2, 'readonly': 1}
            return role_hierarchy.get(membership.role, 0) >= role_hierarchy.get(required_role, 0)
        except ChatRoomMembership.DoesNotExist:
            return False

class ChatMessageViewSet(viewsets.ModelViewSet):
    """مدیریت پیام‌های چت"""
    
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(
            room__memberships__user=user,
            room__memberships__is_active=True,
            is_deleted=False
        ).select_related('sender', 'room').prefetch_related('read_status__user')
    
    def perform_create(self, serializer):
        # بررسی دسترسی ارسال پیام
        room = serializer.validated_data['room']
        if not self._can_send_message(room, self.request.user):
            raise permissions.PermissionDenied("You don't have permission to send messages in this room")
        
        message = serializer.save(sender=self.request.user)
        
        # پردازش منشن‌ها
        self._process_mentions(message)
        
        # ارسال اعلان به اعضا
        self._notify_room_members(message)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """علامت‌گذاری پیام به عنوان خوانده شده"""
        message = self.get_object()
        
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        if not created:
            read_status.read_at = timezone.now()
            read_status.save()
        
        return Response({'message': 'Message marked as read'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """پاسخ به پیام"""
        parent_message = self.get_object()
        content = request.data.get('content')
        
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        reply_message = ChatMessage.objects.create(
            room=parent_message.room,
            sender=request.user,
            content=content,
            reply_to=parent_message
        )
        
        serializer = ChatMessageSerializer(reply_message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def edit(self, request, pk=None):
        """ویرایش پیام"""
        message = self.get_object()
        
        # بررسی دسترسی ویرایش
        if message.sender != request.user:
            return Response({'error': 'You can only edit your own messages'}, status=status.HTTP_403_FORBIDDEN)
        
        content = request.data.get('content')
        if not content:
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message.content = content
        message.is_edited = True
        message.edited_at = timezone.now()
        message.save()
        
        serializer = ChatMessageSerializer(message, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def delete(self, request, pk=None):
        """حذف پیام"""
        message = self.get_object()
        
        # بررسی دسترسی حذف
        if message.sender != request.user and not self._can_moderate_room(message.room, request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        message.is_deleted = True
        message.deleted_at = timezone.now()
        message.save()
        
        return Response({'message': 'Message deleted'}, status=status.HTTP_200_OK)
    
    def _can_send_message(self, room, user):
        """بررسی امکان ارسال پیام"""
        try:
            membership = ChatRoomMembership.objects.get(room=room, user=user, is_active=True)
            return membership.role in ['admin', 'moderator', 'member']
        except ChatRoomMembership.DoesNotExist:
            return False
    
    def _can_moderate_room(self, room, user):
        """بررسی امکان مدیریت اتاق"""
        try:
            membership = ChatRoomMembership.objects.get(room=room, user=user, is_active=True)
            return membership.role in ['admin', 'moderator']
        except ChatRoomMembership.DoesNotExist:
            return False
    
    def _process_mentions(self, message):
        """پردازش منشن‌ها در پیام"""
        import re
        
        # پیدا کردن منشن‌ها (@username)
        mention_pattern = r'@(\w+)'
        mentions = re.findall(mention_pattern, message.content)
        
        for username in mentions:
            try:
                mentioned_user = CustomUser.objects.get(username=username)
                
                # ایجاد منشن
                Mention.objects.create(
                    mentioned_user=mentioned_user,
                    content_object=message,
                    mention_type='message',
                    text=message.content,
                    position=message.content.find(f'@{username}'),
                    created_by=message.sender
                )
                
                # ارسال اعلان
                Notification.objects.create(
                    user=mentioned_user,
                    notification_type='mention',
                    title=f'در پیام منشن شدید',
                    message=f'{message.sender.get_full_name()} شما را در پیام منشن کرد',
                    content_object=message
                )
                
            except CustomUser.DoesNotExist:
                continue
    
    def _notify_room_members(self, message):
        """ارسال اعلان به اعضای اتاق"""
        room_members = ChatRoomMembership.objects.filter(
            room=message.room,
            is_active=True
        ).exclude(user=message.sender)
        
        for membership in room_members:
            Notification.objects.create(
                user=membership.user,
                notification_type='mention',
                title=f'پیام جدید در {message.room.name}',
                message=f'{message.sender.get_full_name()}: {message.content[:100]}...',
                content_object=message
            )

class MentionViewSet(viewsets.ReadOnlyModelViewSet):
    """مدیریت منشن‌ها"""
    
    serializer_class = None  # TODO: Create MentionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Mention.objects.filter(mentioned_user=self.request.user).select_related(
            'mentioned_user', 'created_by', 'content_type'
        ).prefetch_related('content_object')
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """علامت‌گذاری منشن به عنوان خوانده شده"""
        mention = self.get_object()
        mention.mark_as_read()
        return Response({'message': 'Mention marked as read'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """تعداد منشن‌های خوانده نشده"""
        count = Mention.objects.filter(
            mentioned_user=request.user,
            is_read=False
        ).count()
        return Response({'unread_count': count})