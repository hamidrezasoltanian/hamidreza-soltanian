from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class Tag(models.Model):
    """مدل برچسب‌ها"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#2196F3', validators=[
        RegexValidator(regex=r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', message='رنگ باید در فرمت hex باشد')
    ])
    icon = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب‌ها'
        ordering = ['category', 'name']
    
    def __str__(self):
        return self.name

class TaggedItem(models.Model):
    """ارتباط برچسب‌ها با اشیاء مختلف"""
    
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tagged_items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['tag', 'content_type', 'object_id']
        verbose_name = 'آیتم برچسب‌دار'
        verbose_name_plural = 'آیتم‌های برچسب‌دار'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.tag.name} - {self.content_object}"

class TagCategory(models.Model):
    """دسته‌بندی برچسب‌ها"""
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#4CAF50')
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'دسته برچسب'
        verbose_name_plural = 'دسته‌های برچسب'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Mention(models.Model):
    """سیستم منشن کردن کاربران"""
    
    MENTION_TYPES = [
        ('comment', 'نظر'),
        ('task', 'وظیفه'),
        ('message', 'پیام'),
        ('document', 'سند'),
        ('invoice', 'فاکتور'),
        ('customer', 'مشتری'),
    ]
    
    mentioned_user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='mentions')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    mention_type = models.CharField(max_length=20, choices=MENTION_TYPES)
    text = models.TextField()  # متن اطراف منشن
    position = models.PositiveIntegerField()  # موقعیت منشن در متن
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='created_mentions')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'منشن'
        verbose_name_plural = 'منشن‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"@{self.mentioned_user.username} در {self.content_object}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

class Notification(models.Model):
    """سیستم اعلان‌ها"""
    
    NOTIFICATION_TYPES = [
        ('mention', 'منشن'),
        ('task_assigned', 'وظیفه محول شده'),
        ('task_due', 'موعد وظیفه'),
        ('invoice_created', 'فاکتور ایجاد شد'),
        ('customer_updated', 'مشتری به‌روزرسانی شد'),
        ('system', 'سیستم'),
        ('reminder', 'یادآوری'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'پایین'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    ]
    
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # لینک به محتوا
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # متادیتا
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.title}"
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_sent(self):
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()

class ChatRoom(models.Model):
    """اتاق‌های چت"""
    
    ROOM_TYPES = [
        ('direct', 'مستقیم'),
        ('group', 'گروهی'),
        ('channel', 'کانال'),
        ('support', 'پشتیبانی'),
    ]
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='group')
    is_active = models.BooleanField(default=True)
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='created_rooms')
    members = models.ManyToManyField('authentication.CustomUser', through='ChatRoomMembership', related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'اتاق چت'
        verbose_name_plural = 'اتاق‌های چت'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name

class ChatRoomMembership(models.Model):
    """عضویت در اتاق‌های چت"""
    
    ROLE_CHOICES = [
        ('admin', 'مدیر'),
        ('moderator', 'ناظر'),
        ('member', 'عضو'),
        ('readonly', 'فقط خواندن'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='room_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey('authentication.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_to_rooms')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['room', 'user']
        verbose_name = 'عضویت اتاق چت'
        verbose_name_plural = 'عضویت‌های اتاق چت'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.room.name}"

class ChatMessage(models.Model):
    """پیام‌های چت"""
    
    MESSAGE_TYPES = [
        ('text', 'متن'),
        ('image', 'تصویر'),
        ('file', 'فایل'),
        ('system', 'سیستم'),
        ('reminder', 'یادآوری'),
    ]
    
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='sent_messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text')
    content = models.TextField()
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')
    
    # وضعیت پیام
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    
    # متادیتا
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'پیام چت'
        verbose_name_plural = 'پیام‌های چت'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.content[:50]}..."

class MessageReadStatus(models.Model):
    """وضعیت خواندن پیام‌ها"""
    
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='read_status')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='message_reads')
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['message', 'user']
        verbose_name = 'وضعیت خواندن پیام'
        verbose_name_plural = 'وضعیت‌های خواندن پیام'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.message.content[:30]}"

class Task(models.Model):
    """وظایف و کارها"""
    
    PRIORITY_LEVELS = [
        ('low', 'پایین'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('in_progress', 'در حال انجام'),
        ('completed', 'تکمیل شده'),
        ('cancelled', 'لغو شده'),
        ('on_hold', 'متوقف'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # مسئولان
    assigned_to = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='created_tasks')
    
    # تاریخ‌ها
    due_date = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # متادیتا
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'وظیفه'
        verbose_name_plural = 'وظایف'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def is_overdue(self):
        if self.due_date and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.due_date
        return False

class CalendarEvent(models.Model):
    """رویدادهای تقویم"""
    
    EVENT_TYPES = [
        ('meeting', 'جلسه'),
        ('task', 'وظیفه'),
        ('reminder', 'یادآوری'),
        ('holiday', 'تعطیل'),
        ('personal', 'شخصی'),
        ('business', 'تجاری'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='meeting')
    
    # زمان‌بندی
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_all_day = models.BooleanField(default=False)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)
    
    # شرکت‌کنندگان
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='created_events')
    attendees = models.ManyToManyField('authentication.CustomUser', through='EventAttendance', related_name='events')
    
    # مکان و لینک
    location = models.CharField(max_length=200, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)
    
    # تنظیمات
    is_private = models.BooleanField(default=False)
    reminder_minutes = models.PositiveIntegerField(default=15)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'رویداد تقویم'
        verbose_name_plural = 'رویدادهای تقویم'
        ordering = ['start_time']
    
    def __str__(self):
        return self.title

class EventAttendance(models.Model):
    """حضور در رویدادها"""
    
    ATTENDANCE_STATUS = [
        ('attending', 'حاضر'),
        ('maybe', 'احتمالاً'),
        ('declined', 'رد'),
        ('not_responded', 'پاسخ نداده'),
    ]
    
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='attendance')
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='event_attendance')
    status = models.CharField(max_length=20, choices=ATTENDANCE_STATUS, default='not_responded')
    responded_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['event', 'user']
        verbose_name = 'حضور در رویداد'
        verbose_name_plural = 'حضور در رویدادها'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.event.title}"

class Reminder(models.Model):
    """یادآوری‌ها"""
    
    REMINDER_TYPES = [
        ('task', 'وظیفه'),
        ('event', 'رویداد'),
        ('custom', 'سفارشی'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES, default='custom')
    
    # زمان‌بندی
    remind_at = models.DateTimeField()
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)
    
    # کاربران
    user = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='reminders')
    created_by = models.ForeignKey('authentication.CustomUser', on_delete=models.CASCADE, related_name='created_reminders')
    
    # لینک به محتوا
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # وضعیت
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'یادآوری'
        verbose_name_plural = 'یادآوری‌ها'
        ordering = ['remind_at']
    
    def __str__(self):
        return self.title