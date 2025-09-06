from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from customers.models import Customer
from personnel.models import Personnel
from products.models import Product


class SalesProcess(models.Model):
    """فرایند فروش"""
    
    PROCESS_TYPES = [
        ('lead', 'سرنخ'),
        ('opportunity', 'فرصت'),
        ('proposal', 'پیشنهاد'),
        ('negotiation', 'مذاکره'),
        ('closed_won', 'بسته شده - موفق'),
        ('closed_lost', 'بسته شده - ناموفق'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'پایین'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
        ('urgent', 'فوری'),
    ]
    
    # اطلاعات اصلی
    process_name = models.CharField(max_length=200, verbose_name='نام فرایند')
    process_type = models.CharField(
        max_length=15, 
        choices=PROCESS_TYPES, 
        verbose_name='نوع فرایند'
    )
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_LEVELS, 
        default='medium',
        verbose_name='اولویت'
    )
    
    # مشتری
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='sales_processes',
        verbose_name='مشتری'
    )
    contact_person = models.ForeignKey(
        Personnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='شخص تماس'
    )
    
    # مبالغ
    estimated_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='ارزش تخمینی'
    )
    actual_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='ارزش واقعی'
    )
    probability = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0), MinValueValidator(100)],
        verbose_name='احتمال موفقیت (%)'
    )
    
    # تاریخ‌ها
    start_date = models.DateField(default=timezone.now, verbose_name='تاریخ شروع')
    expected_close_date = models.DateField(blank=True, null=True, verbose_name='تاریخ بسته شدن مورد انتظار')
    actual_close_date = models.DateField(blank=True, null=True, verbose_name='تاریخ بسته شدن واقعی')
    
    # اطلاعات اضافی
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    # اطلاعات سیستم
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    assigned_to = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='assigned_processes',
        verbose_name='واگذار شده به'
    )
    
    class Meta:
        verbose_name = 'فرایند فروش'
        verbose_name_plural = 'فرایندهای فروش'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['process_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['start_date']),
        ]
    
    def __str__(self):
        return f"{self.process_name} - {self.customer.full_name}"
    
    @property
    def weighted_value(self):
        """ارزش وزنی فرایند"""
        return (self.estimated_value * self.probability) / 100


class ProcessStage(models.Model):
    """مراحل فرایند"""
    
    process = models.ForeignKey(
        SalesProcess, 
        on_delete=models.CASCADE, 
        related_name='stages',
        verbose_name='فرایند'
    )
    stage_name = models.CharField(max_length=200, verbose_name='نام مرحله')
    stage_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب مرحله')
    is_completed = models.BooleanField(default=False, verbose_name='تکمیل شده')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    completed_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        verbose_name='تکمیل شده توسط'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    class Meta:
        verbose_name = 'مرحله فرایند'
        verbose_name_plural = 'مراحل فرایند'
        ordering = ['process', 'stage_order']
    
    def __str__(self):
        return f"{self.process.process_name} - {self.stage_name}"


class ProcessActivity(models.Model):
    """فعالیت‌های فرایند"""
    
    ACTIVITY_TYPES = [
        ('call', 'تماس تلفنی'),
        ('email', 'ایمیل'),
        ('meeting', 'جلسه'),
        ('visit', 'بازدید'),
        ('proposal', 'ارسال پیشنهاد'),
        ('follow_up', 'پیگیری'),
        ('other', 'سایر'),
    ]
    
    process = models.ForeignKey(
        SalesProcess, 
        on_delete=models.CASCADE, 
        related_name='activities',
        verbose_name='فرایند'
    )
    activity_type = models.CharField(
        max_length=15, 
        choices=ACTIVITY_TYPES, 
        verbose_name='نوع فعالیت'
    )
    subject = models.CharField(max_length=200, verbose_name='موضوع')
    description = models.TextField(verbose_name='توضیحات')
    activity_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ فعالیت')
    duration = models.PositiveIntegerField(
        blank=True, 
        null=True,
        help_text='مدت زمان به دقیقه',
        verbose_name='مدت زمان'
    )
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'فعالیت فرایند'
        verbose_name_plural = 'فعالیت‌های فرایند'
        ordering = ['-activity_date']
    
    def __str__(self):
        return f"{self.process.process_name} - {self.subject}"


class Lead(models.Model):
    """سرنخ‌های فروش"""
    
    LEAD_SOURCES = [
        ('website', 'وب‌سایت'),
        ('referral', 'معرفی'),
        ('advertisement', 'تبلیغات'),
        ('cold_call', 'تماس سرد'),
        ('email', 'ایمیل'),
        ('social_media', 'شبکه‌های اجتماعی'),
        ('event', 'رویداد'),
        ('other', 'سایر'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'جدید'),
        ('contacted', 'تماس گرفته شده'),
        ('qualified', 'صلاحیت‌دار'),
        ('unqualified', 'غیرصلاحیت‌دار'),
        ('converted', 'تبدیل شده'),
        ('lost', 'از دست رفته'),
    ]
    
    # اطلاعات اصلی
    lead_name = models.CharField(max_length=200, verbose_name='نام سرنخ')
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='نام شرکت'
    )
    contact_person = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='شخص تماس'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='تلفن')
    
    # منبع و وضعیت
    source = models.CharField(
        max_length=15, 
        choices=LEAD_SOURCES, 
        verbose_name='منبع'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='new',
        verbose_name='وضعیت'
    )
    
    # اطلاعات کسب‌وکار
    industry = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='صنعت'
    )
    company_size = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='اندازه شرکت'
    )
    estimated_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='ارزش تخمینی'
    )
    
    # اطلاعات اضافی
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    # تاریخ‌ها
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    converted_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تبدیل')
    
    # اطلاعات سیستم
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    assigned_to = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='assigned_leads',
        verbose_name='واگذار شده به'
    )
    converted_to_customer = models.ForeignKey(
        Customer, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='converted_from_lead',
        verbose_name='تبدیل شده به مشتری'
    )
    
    class Meta:
        verbose_name = 'سرنخ'
        verbose_name_plural = 'سرنخ‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['source']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.lead_name} - {self.company_name or ''}"


class Task(models.Model):
    """وظایف"""
    
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
    ]
    
    # اطلاعات اصلی
    title = models.CharField(max_length=200, verbose_name='عنوان')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    priority = models.CharField(
        max_length=10, 
        choices=PRIORITY_LEVELS, 
        default='medium',
        verbose_name='اولویت'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    
    # تاریخ‌ها
    due_date = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ سررسید')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تکمیل')
    
    # اطلاعات سیستم
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    assigned_to = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='واگذار شده به'
    )
    
    # مرجع
    reference_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='نوع مرجع'
    )
    reference_id = models.PositiveIntegerField(
        blank=True, 
        null=True,
        verbose_name='شناسه مرجع'
    )
    
    class Meta:
        verbose_name = 'وظیفه'
        verbose_name_plural = 'وظایف'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['assigned_to']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"