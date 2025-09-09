from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from datetime import timedelta
import json


class EventType(models.TextChoices):
    PAGE_VIEW = 'page_view', 'Page View'
    BUTTON_CLICK = 'button_click', 'Button Click'
    FORM_SUBMIT = 'form_submit', 'Form Submit'
    API_CALL = 'api_call', 'API Call'
    USER_LOGIN = 'user_login', 'User Login'
    USER_LOGOUT = 'user_logout', 'User Logout'
    CUSTOMER_CREATED = 'customer_created', 'Customer Created'
    CUSTOMER_UPDATED = 'customer_updated', 'Customer Updated'
    INVOICE_CREATED = 'invoice_created', 'Invoice Created'
    PRODUCT_VIEWED = 'product_viewed', 'Product Viewed'
    SEARCH_PERFORMED = 'search_performed', 'Search Performed'
    EXPORT_PERFORMED = 'export_performed', 'Export Performed'
    IMPORT_PERFORMED = 'import_performed', 'Import Performed'


class AnalyticsEvent(models.Model):
    """Track user interactions and system events"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=50, choices=EventType.choices, db_index=True)
    event_name = models.CharField(max_length=100, db_index=True)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Event data
    properties = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    # Location and device info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Timestamps
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['session_id', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type}: {self.event_name} - {self.timestamp}"


class UserSession(models.Model):
    """Track user sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    referrer = models.URLField(blank=True)
    
    # Session data
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    page_views = models.PositiveIntegerField(default=0)
    events_count = models.PositiveIntegerField(default=0)
    
    # Device and location info
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['user', 'start_time']),
            models.Index(fields=['session_id']),
        ]
    
    def __str__(self):
        return f"Session {self.session_id} - {self.user or 'Anonymous'}"
    
    def end_session(self):
        """End the session and calculate duration"""
        self.end_time = timezone.now()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.save()


class PageView(models.Model):
    """Track page views"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(UserSession, on_delete=models.CASCADE)
    page_url = models.URLField()
    page_title = models.CharField(max_length=200, blank=True)
    referrer = models.URLField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['session', 'timestamp']),
        ]


class PerformanceMetric(models.Model):
    """Track performance metrics"""
    METRIC_TYPES = [
        ('api_response_time', 'API Response Time'),
        ('page_load_time', 'Page Load Time'),
        ('database_query_time', 'Database Query Time'),
        ('cache_hit_rate', 'Cache Hit Rate'),
        ('memory_usage', 'Memory Usage'),
        ('cpu_usage', 'CPU Usage'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, db_index=True)
    metric_name = models.CharField(max_length=100, db_index=True)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default='ms')
    
    # Context
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    endpoint = models.CharField(max_length=200, blank=True)
    
    # Additional data
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]


class BusinessMetric(models.Model):
    """Track business metrics"""
    METRIC_TYPES = [
        ('revenue', 'Revenue'),
        ('customers_count', 'Customers Count'),
        ('invoices_count', 'Invoices Count'),
        ('products_count', 'Products Count'),
        ('conversion_rate', 'Conversion Rate'),
        ('retention_rate', 'Retention Rate'),
        ('churn_rate', 'Churn Rate'),
    ]
    
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, db_index=True)
    value = models.DecimalField(max_digits=15, decimal_places=2)
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    
    # Additional context
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-period_start']
        indexes = [
            models.Index(fields=['metric_type', 'period_start']),
        ]
        unique_together = ['metric_type', 'period_start', 'period_end']


class Report(models.Model):
    """Store generated reports"""
    REPORT_TYPES = [
        ('user_activity', 'User Activity'),
        ('sales_performance', 'Sales Performance'),
        ('customer_analytics', 'Customer Analytics'),
        ('product_analytics', 'Product Analytics'),
        ('system_performance', 'System Performance'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Report configuration
    parameters = models.JSONField(default=dict, blank=True)
    filters = models.JSONField(default=dict, blank=True)
    
    # Generated report data
    data = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=500, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Schedule
    is_scheduled = models.BooleanField(default=False)
    schedule_cron = models.CharField(max_length=100, blank=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type', 'created_at']),
            models.Index(fields=['created_by', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.report_type})"