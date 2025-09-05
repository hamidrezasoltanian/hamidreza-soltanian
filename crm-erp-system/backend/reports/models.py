from django.db import models
from django.utils import timezone


class ReportTemplate(models.Model):
    """قالب‌های گزارش"""
    
    REPORT_TYPES = [
        ('financial', 'مالی'),
        ('sales', 'فروش'),
        ('inventory', 'انبار'),
        ('customer', 'مشتری'),
        ('tax', 'مالیاتی'),
        ('custom', 'سفارشی'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام قالب')
    report_type = models.CharField(
        max_length=15, 
        choices=REPORT_TYPES, 
        verbose_name='نوع گزارش'
    )
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    template_file = models.FileField(
        upload_to='report_templates/', 
        verbose_name='فایل قالب'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'قالب گزارش'
        verbose_name_plural = 'قالب‌های گزارش'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ReportSchedule(models.Model):
    """زمان‌بندی گزارش‌ها"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'روزانه'),
        ('weekly', 'هفتگی'),
        ('monthly', 'ماهانه'),
        ('quarterly', 'فصلانه'),
        ('yearly', 'سالانه'),
        ('custom', 'سفارشی'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='نام زمان‌بندی')
    template = models.ForeignKey(
        ReportTemplate, 
        on_delete=models.CASCADE, 
        related_name='schedules',
        verbose_name='قالب گزارش'
    )
    frequency = models.CharField(
        max_length=15, 
        choices=FREQUENCY_CHOICES, 
        verbose_name='فرکانس'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    next_run = models.DateTimeField(verbose_name='اجرای بعدی')
    last_run = models.DateTimeField(blank=True, null=True, verbose_name='آخرین اجرا')
    email_recipients = models.TextField(
        blank=True, 
        null=True,
        help_text='ایمیل‌ها را با کاما جدا کنید',
        verbose_name='گیرندگان ایمیل'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'زمان‌بندی گزارش'
        verbose_name_plural = 'زمان‌بندی گزارش‌ها'
        ordering = ['next_run']
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"


class ReportExecution(models.Model):
    """اجرای گزارش‌ها"""
    
    STATUS_CHOICES = [
        ('pending', 'در انتظار'),
        ('running', 'در حال اجرا'),
        ('completed', 'تکمیل شده'),
        ('failed', 'ناموفق'),
        ('cancelled', 'لغو شده'),
    ]
    
    schedule = models.ForeignKey(
        ReportSchedule, 
        on_delete=models.CASCADE, 
        related_name='executions',
        verbose_name='زمان‌بندی'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='pending',
        verbose_name='وضعیت'
    )
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='شروع شده در')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='تکمیل شده در')
    file_path = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='مسیر فایل'
    )
    error_message = models.TextField(blank=True, null=True, verbose_name='پیام خطا')
    
    class Meta:
        verbose_name = 'اجرای گزارش'
        verbose_name_plural = 'اجراهای گزارش'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.schedule.name} - {self.get_status_display()}"


class Dashboard(models.Model):
    """داشبوردها"""
    
    name = models.CharField(max_length=200, verbose_name='نام داشبورد')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    is_public = models.BooleanField(default=False, verbose_name='عمومی')
    is_default = models.BooleanField(default=False, verbose_name='پیش‌فرض')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.CASCADE, 
        related_name='created_dashboards',
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'داشبورد'
        verbose_name_plural = 'داشبوردها'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DashboardWidget(models.Model):
    """ویجت‌های داشبورد"""
    
    WIDGET_TYPES = [
        ('chart', 'نمودار'),
        ('table', 'جدول'),
        ('metric', 'معیار'),
        ('gauge', 'سنج'),
        ('map', 'نقشه'),
        ('text', 'متن'),
    ]
    
    CHART_TYPES = [
        ('line', 'خطی'),
        ('bar', 'ستونی'),
        ('pie', 'دایره‌ای'),
        ('area', 'ناحیه‌ای'),
        ('scatter', 'پراکندگی'),
        ('donut', 'دونات'),
    ]
    
    dashboard = models.ForeignKey(
        Dashboard, 
        on_delete=models.CASCADE, 
        related_name='widgets',
        verbose_name='داشبورد'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان')
    widget_type = models.CharField(
        max_length=10, 
        choices=WIDGET_TYPES, 
        verbose_name='نوع ویجت'
    )
    chart_type = models.CharField(
        max_length=10, 
        choices=CHART_TYPES, 
        blank=True, 
        null=True,
        verbose_name='نوع نمودار'
    )
    data_source = models.CharField(max_length=200, verbose_name='منبع داده')
    query = models.TextField(verbose_name='کوئری')
    position_x = models.PositiveIntegerField(default=0, verbose_name='موقعیت X')
    position_y = models.PositiveIntegerField(default=0, verbose_name='موقعیت Y')
    width = models.PositiveIntegerField(default=4, verbose_name='عرض')
    height = models.PositiveIntegerField(default=3, verbose_name='ارتفاع')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        verbose_name = 'ویجت داشبورد'
        verbose_name_plural = 'ویجت‌های داشبورد'
        ordering = ['dashboard', 'sort_order']
    
    def __str__(self):
        return f"{self.dashboard.name} - {self.title}"