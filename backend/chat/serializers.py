from rest_framework import serializers
from .models import ChatRoom, ChatMessage, MessageReadStatus, ChatRoomMembership
from authentication.models import CustomUser
from common.models import Mention, Notification

class UserBasicSerializer(serializers.ModelSerializer):
    """سریالایزر پایه کاربر"""
    
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'avatar_url', 'is_online']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None

class ChatRoomMembershipSerializer(serializers.ModelSerializer):
    """سریالایزر عضویت در اتاق چت"""
    
    user = UserBasicSerializer(read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = ChatRoomMembership
        fields = ['id', 'user', 'role', 'role_display', 'joined_at', 'is_active']

class ChatMessageSerializer(serializers.ModelSerializer):
    """سریالایزر پیام‌های چت"""
    
    sender = UserBasicSerializer(read_only=True)
    reply_to = serializers.SerializerMethodField()
    read_by = serializers.SerializerMethodField()
    is_read_by_me = serializers.SerializerMethodField()
    mentions = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = [
            'id', 'sender', 'message_type', 'content', 'file', 'reply_to',
            'is_edited', 'is_deleted', 'edited_at', 'read_by', 'is_read_by_me',
            'mentions', 'created_at', 'updated_at'
        ]
        read_only_fields = ['sender', 'created_at', 'updated_at']
    
    def get_reply_to(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'content': obj.reply_to.content[:100] + '...' if len(obj.reply_to.content) > 100 else obj.reply_to.content,
                'sender': UserBasicSerializer(obj.reply_to.sender).data
            }
        return None
    
    def get_read_by(self, obj):
        read_statuses = obj.read_status.all()
        return [
            {
                'user': UserBasicSerializer(status.user).data,
                'read_at': status.read_at
            }
            for status in read_statuses
        ]
    
    def get_is_read_by_me(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.read_status.filter(user=request.user).exists()
        return False
    
    def get_mentions(self, obj):
        mentions = Mention.objects.filter(
            content_type__model='chatmessage',
            object_id=obj.id
        ).select_related('mentioned_user')
        
        return [
            {
                'id': mention.id,
                'user': UserBasicSerializer(mention.mentioned_user).data,
                'text': mention.text,
                'position': mention.position,
                'is_read': mention.is_read
            }
            for mention in mentions
        ]

class CreateChatMessageSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد پیام چت"""
    
    class Meta:
        model = ChatMessage
        fields = ['room', 'message_type', 'content', 'file', 'reply_to']
    
    def validate_room(self, value):
        """بررسی دسترسی به اتاق"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = ChatRoomMembership.objects.get(
                    room=value,
                    user=request.user,
                    is_active=True
                )
                if membership.role not in ['admin', 'moderator', 'member']:
                    raise serializers.ValidationError("You don't have permission to send messages in this room")
            except ChatRoomMembership.DoesNotExist:
                raise serializers.ValidationError("You are not a member of this room")
        return value

class ChatRoomSerializer(serializers.ModelSerializer):
    """سریالایزر اتاق‌های چت"""
    
    members = ChatRoomMembershipSerializer(source='memberships', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    my_role = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatRoom
        fields = [
            'id', 'name', 'description', 'room_type', 'is_active', 'is_private',
            'members', 'last_message', 'unread_count', 'member_count', 'my_role',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_last_message(self, obj):
        last_message = obj.messages.filter(is_deleted=False).order_by('-created_at').first()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender': UserBasicSerializer(last_message.sender).data,
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_deleted=False,
                sender__ne=request.user
            ).exclude(
                read_status__user=request.user
            ).count()
        return 0
    
    def get_member_count(self, obj):
        return obj.memberships.filter(is_active=True).count()
    
    def get_my_role(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = ChatRoomMembership.objects.get(
                    room=obj,
                    user=request.user,
                    is_active=True
                )
                return membership.role
            except ChatRoomMembership.DoesNotExist:
                return None
        return None

class CreateChatRoomSerializer(serializers.ModelSerializer):
    """سریالایزر ایجاد اتاق چت"""
    
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = ChatRoom
        fields = ['name', 'description', 'room_type', 'is_private', 'member_ids']
    
    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        room = ChatRoom.objects.create(
            **validated_data,
            created_by=self.context['request'].user
        )
        
        # اضافه کردن سازنده به عنوان ادمین
        ChatRoomMembership.objects.create(
            room=room,
            user=self.context['request'].user,
            role='admin'
        )
        
        # اضافه کردن اعضای دیگر
        for user_id in member_ids:
            try:
                user = CustomUser.objects.get(id=user_id)
                ChatRoomMembership.objects.create(
                    room=room,
                    user=user,
                    role='member',
                    invited_by=self.context['request'].user
                )
            except CustomUser.DoesNotExist:
                continue
        
        return room

class MessageReadStatusSerializer(serializers.ModelSerializer):
    """سریالایزر وضعیت خواندن پیام‌ها"""
    
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'user', 'read_at']

class MentionSerializer(serializers.ModelSerializer):
    """سریالایزر منشن‌ها"""
    
    mentioned_user = UserBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    content_object = serializers.SerializerMethodField()
    mention_type_display = serializers.CharField(source='get_mention_type_display', read_only=True)
    
    class Meta:
        model = Mention
        fields = [
            'id', 'mentioned_user', 'mention_type', 'mention_type_display',
            'text', 'position', 'is_read', 'read_at', 'created_by',
            'content_object', 'created_at'
        ]
        read_only_fields = ['created_by', 'created_at']
    
    def get_content_object(self, obj):
        if obj.content_object:
            return {
                'id': obj.content_object.id,
                'type': obj.content_type.model,
                'title': str(obj.content_object)[:100]
            }
        return None

class NotificationSerializer(serializers.ModelSerializer):
    """سریالایزر اعلان‌ها"""
    
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    content_object = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'notification_type_display',
            'title', 'message', 'priority', 'priority_display',
            'is_read', 'is_sent', 'read_at', 'sent_at',
            'content_object', 'metadata', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_content_object(self, obj):
        if obj.content_object:
            return {
                'id': obj.content_object.id,
                'type': obj.content_type.model,
                'title': str(obj.content_object)[:100]
            }
        return None

class UserSearchSerializer(serializers.ModelSerializer):
    """سریالایزر جستجوی کاربران"""
    
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'avatar_url', 'email', 'department', 'position']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None