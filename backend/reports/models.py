from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from authentication.models import CustomUser
from common.models import Tag, TaggedItem
import json

class ReportTemplate(models.Model):
    """قالب‌های گزارش"""
    
    REPORT_TYPES = [
        ('customers', 'مشتریان'),
        ('invoices', 'فاکتورها'),
        ('products', 'محصولات'),
        ('inventory', 'انبار'),
        ('sales', 'فروش'),
        ('financial', 'مالی'),
        ('custom', 'سفارشی'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='custom')
    query = models.TextField(help_text="SQL query or JSON configuration")
    parameters = models.JSONField(default=dict, blank=True)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'قالب گزارش'
        verbose_name_plural = 'قالب‌های گزارش'
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Report(models.Model):
    """گزارش‌ها"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports')
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_reports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'گزارش'
        verbose_name_plural = 'گزارش‌ها'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ReportExecution(models.Model):
    """اجرای گزارش‌ها"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('running', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='executions')
    executed_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='report_executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    filters = models.JSONField(default=dict, blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)
    execution_time = models.DurationField(blank=True, null=True)
    record_count = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'اجرای گزارش'
        verbose_name_plural = 'اجراهای گزارش'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.report.name} - {self.executed_by.get_full_name()}"
    
    @property
    def duration(self):
        if self.completed_at and self.started_at:
            return self.completed_at - self.started_at
        return None

class ReportSchedule(models.Model):
    """زمان‌بندی گزارش‌ها"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('quarterly', 'فصلی'),
        ('yearly', 'سالانه'),
        ('custom', 'سفارشی'),
    ]
    
    DAY_CHOICES = [
        (0, 'دوشنبه'),
        (1, 'سه‌شنبه'),
        (2, 'چهارشنبه'),
        (3, 'پنج‌شنبه'),
        (4, 'جمعه'),
        (5, 'شنبه'),
        (6, 'یکشنبه'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='schedules')
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    day_of_week = models.IntegerField(choices=DAY_CHOICES, blank=True, null=True)
    day_of_month = models.PositiveIntegerField(blank=True, null=True)
    hour = models.PositiveIntegerField(default=9)  # ساعت اجرا
    minute = models.PositiveIntegerField(default=0)
    timezone = models.CharField(max_length=50, default='Asia/Tehran')
    
    # تنظیمات ارسال
    send_email = models.BooleanField(default=True)
    email_recipients = models.JSONField(default=list, blank=True)
    email_subject = models.CharField(max_length=200, blank=True, null=True)
    email_template = models.TextField(blank=True, null=True)
    
    # فیلترهای ثابت
    fixed_filters = models.JSONField(default=dict, blank=True)
    
    # وضعیت
    is_active = models.BooleanField(default=True)
    last_executed = models.DateTimeField(blank=True, null=True)
    next_execution = models.DateTimeField(blank=True, null=True)
    
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'زمان‌بندی گزارش'
        verbose_name_plural = 'زمان‌بندی‌های گزارش'
        ordering = ['next_execution']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"

class ReportExport(models.Model):
    """صادرات گزارش‌ها"""
    
    FORMAT_CHOICES = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    ]
    
    execution = models.ForeignKey(ReportExecution, on_delete=models.CASCADE, related_name='exports')
    format_type = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    file_path = models.CharField(max_length=500)
    file_size = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'صادرات گزارش'
        verbose_name_plural = 'صادرات‌های گزارش'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.execution.report.name} - {self.get_format_type_display()}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class ReportFilter(models.Model):
    """فیلترهای گزارش"""
    
    FILTER_TYPES = [
        ('text', 'متن'),
        ('number', 'عدد'),
        ('date', 'تاریخ'),
        ('datetime', 'تاریخ و زمان'),
        ('select', 'انتخابی'),
        ('multiselect', 'چند انتخابی'),
        ('boolean', 'بله/خیر'),
        ('range', 'بازه'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='filters')
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=200)
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPES)
    field_name = models.CharField(max_length=100)  # نام فیلد در دیتابیس
    options = models.JSONField(default=list, blank=True)  # گزینه‌های انتخابی
    default_value = models.CharField(max_length=200, blank=True, null=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'فیلتر گزارش'
        verbose_name_plural = 'فیلترهای گزارش'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.template.name} - {self.label}"

class ReportDashboard(models.Model):
    """داشبوردهای گزارش"""
    
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    layout = models.JSONField(default=dict, blank=True)  # چیدمان ویجت‌ها
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_dashboards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'داشبورد گزارش'
        verbose_name_plural = 'داشبوردهای گزارش'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

class ReportWidget(models.Model):
    """ویجت‌های گزارش"""
    
    WIDGET_TYPES = [
        ('chart', 'نمودار'),
        ('table', 'جدول'),
        ('metric', 'متریک'),
        ('kpi', 'KPI'),
        ('text', 'متن'),
    ]
    
    CHART_TYPES = [
        ('line', 'خطی'),
        ('bar', 'ستونی'),
        ('pie', 'دایره‌ای'),
        ('area', 'ناحیه‌ای'),
        ('scatter', 'پراکندگی'),
    ]
    
    dashboard = models.ForeignKey(ReportDashboard, on_delete=models.CASCADE, related_name='widgets')
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='widgets')
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    position = models.JSONField(default=dict, blank=True)  # موقعیت در داشبورد
    size = models.JSONField(default=dict, blank=True)  # اندازه ویجت
    config = models.JSONField(default=dict, blank=True)  # تنظیمات ویجت
    filters = models.JSONField(default=dict, blank=True)  # فیلترهای خاص ویجت
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'ویجت گزارش'
        verbose_name_plural = 'ویجت‌های گزارش'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"

class ReportAccess(models.Model):
    """دسترسی‌های گزارش"""
    
    PERMISSION_TYPES = [
        ('view', 'مشاهده'),
        ('execute', 'اجرا'),
        ('export', 'صادرات'),
        ('schedule', 'زمان‌بندی'),
        ('admin', 'مدیریت'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='accesses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='report_accesses', blank=True, null=True)
    group = models.ForeignKey('authentication.UserGroup', on_delete=models.CASCADE, related_name='report_accesses', blank=True, null=True)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    granted_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='granted_report_accesses')
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'دسترسی گزارش'
        verbose_name_plural = 'دسترسی‌های گزارش'
        unique_together = ['report', 'user', 'permission_type']
    
    def __str__(self):
        return f"{self.report.name} - {self.user.get_full_name() if self.user else self.group.name} - {self.get_permission_type_display()}"
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False