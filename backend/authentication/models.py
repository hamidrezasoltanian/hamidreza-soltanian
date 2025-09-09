from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    """مدل کاربر سفارشی با قابلیت‌های پیشرفته"""
    
    # اطلاعات شخصی
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="شماره تلفن باید در فرمت صحیح وارد شود.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    national_id = models.CharField(max_length=10, blank=True, null=True, unique=True)
    birth_date = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # اطلاعات شغلی
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='subordinates')
    
    # تنظیمات کاربر
    timezone = models.CharField(max_length=50, default='Asia/Tehran')
    language = models.CharField(max_length=10, default='fa')
    is_2fa_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=16, blank=True, null=True)
    
    # وضعیت
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    
    # متادیتا
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name or self.username

class Role(models.Model):
    """مدل نقش‌ها"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#2196F3')  # Hex color
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'نقش'
        verbose_name_plural = 'نقش‌ها'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Permission(models.Model):
    """مدل مجوزها"""
    
    PERMISSION_TYPES = [
        ('view', 'مشاهده'),
        ('add', 'افزودن'),
        ('change', 'ویرایش'),
        ('delete', 'حذف'),
        ('export', 'صادرات'),
        ('import', 'واردات'),
        ('approve', 'تایید'),
        ('reject', 'رد'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    codename = models.CharField(max_length=100, unique=True)
    content_type = models.CharField(max_length=100)  # app.model
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'مجوز'
        verbose_name_plural = 'مجوزها'
        ordering = ['content_type', 'permission_type']
        unique_together = ['codename', 'content_type']
    
    def __str__(self):
        return f"{self.name} ({self.content_type})"

class RolePermission(models.Model):
    """ارتباط نقش‌ها و مجوزها"""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        unique_together = ['role', 'permission']
        verbose_name = 'مجوز نقش'
        verbose_name_plural = 'مجوزهای نقش‌ها'
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"

class UserRole(models.Model):
    """ارتباط کاربران و نقش‌ها"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'role']
        verbose_name = 'نقش کاربر'
        verbose_name_plural = 'نقش‌های کاربران'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role.name}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class UserGroup(models.Model):
    """گروه‌های کاربری"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=7, default='#4CAF50')
    icon = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'گروه کاربری'
        verbose_name_plural = 'گروه‌های کاربری'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class UserGroupMembership(models.Model):
    """عضویت در گروه‌های کاربری"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='group_memberships')
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='members')
    joined_at = models.DateTimeField(auto_now_add=True)
    joined_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_to_groups')
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'group']
        verbose_name = 'عضویت گروه'
        verbose_name_plural = 'عضویت‌های گروه'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group.name}"

class UserSession(models.Model):
    """جلسات کاربران"""
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = 'جلسه کاربر'
        verbose_name_plural = 'جلسات کاربران'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.session_key[:8]}..."
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

class UserActivity(models.Model):
    """فعالیت‌های کاربران"""
    
    ACTIVITY_TYPES = [
        ('login', 'ورود'),
        ('logout', 'خروج'),
        ('create', 'ایجاد'),
        ('update', 'ویرایش'),
        ('delete', 'حذف'),
        ('view', 'مشاهده'),
        ('export', 'صادرات'),
        ('import', 'واردات'),
        ('approve', 'تایید'),
        ('reject', 'رد'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'فعالیت کاربر'
        verbose_name_plural = 'فعالیت‌های کاربران'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_activity_type_display()}"

class UserPreference(models.Model):
    """تنظیمات کاربران"""
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    theme = models.CharField(max_length=20, default='auto', choices=[
        ('light', 'روشن'),
        ('dark', 'تیره'),
        ('auto', 'خودکار'),
    ])
    language = models.CharField(max_length=10, default='fa')
    timezone = models.CharField(max_length=50, default='Asia/Tehran')
    date_format = models.CharField(max_length=20, default='%Y/%m/%d')
    time_format = models.CharField(max_length=20, default='24')
    currency = models.CharField(max_length=3, default='IRR')
    notifications = models.JSONField(default=dict, blank=True)
    dashboard_layout = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'تنظیمات کاربر'
        verbose_name_plural = 'تنظیمات کاربران'
    
    def __str__(self):
        return f"تنظیمات {self.user.get_full_name()}"