from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from customers.models import Customer


class TaxPayer(models.Model):
    """مودی مالیاتی"""
    
    TAXPAYER_TYPES = [
        ('individual', 'حقیقی'),
        ('legal', 'حقوقی'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('suspended', 'معلق'),
        ('blacklisted', 'لیست سیاه'),
    ]
    
    # اطلاعات اصلی
    taxpayer_id = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='شناسه مودی'
    )
    taxpayer_type = models.CharField(
        max_length=10, 
        choices=TAXPAYER_TYPES, 
        verbose_name='نوع مودی'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='وضعیت'
    )
    
    # ارتباط با مشتری
    customer = models.OneToOneField(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='taxpayer',
        verbose_name='مشتری'
    )
    
    # اطلاعات مالیاتی
    tax_office_code = models.CharField(
        max_length=10, 
        verbose_name='کد اداره مالیات'
    )
    tax_office_name = models.CharField(
        max_length=200, 
        verbose_name='نام اداره مالیات'
    )
    economic_code = models.CharField(
        max_length=12, 
        unique=True,
        validators=[MinValueValidator(0)],
        verbose_name='کد اقتصادی'
    )
    national_id = models.CharField(
        max_length=10, 
        unique=True,
        validators=[MinValueValidator(0)],
        verbose_name='شناسه ملی'
    )
    registration_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='شماره ثبت'
    )
    
    # اطلاعات مالی
    annual_turnover = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='گردش مالی سالانه'
    )
    tax_exempt = models.BooleanField(default=False, verbose_name='معاف از مالیات')
    tax_exemption_reason = models.TextField(
        blank=True, 
        null=True,
        verbose_name='دلیل معافیت'
    )
    
    # اطلاعات سیستم
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'مودی مالیاتی'
        verbose_name_plural = 'مودیان مالیاتی'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['taxpayer_id']),
            models.Index(fields=['economic_code']),
            models.Index(fields=['national_id']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.customer.full_name} ({self.taxpayer_id})"


class TaxRate(models.Model):
    """نرخ‌های مالیاتی"""
    
    TAX_TYPES = [
        ('vat', 'مالیات بر ارزش افزوده'),
        ('income', 'مالیات بر درآمد'),
        ('corporate', 'مالیات بر درآمد اشخاص حقوقی'),
        ('withholding', 'مالیات تکلیفی'),
        ('stamp', 'تمبر'),
        ('other', 'سایر'),
    ]
    
    tax_type = models.CharField(
        max_length=15, 
        choices=TAX_TYPES, 
        verbose_name='نوع مالیات'
    )
    name = models.CharField(max_length=200, verbose_name='نام نرخ')
    rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='نرخ (درصد)'
    )
    effective_from = models.DateField(verbose_name='اعتبار از تاریخ')
    effective_to = models.DateField(
        blank=True, 
        null=True,
        verbose_name='اعتبار تا تاریخ'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'نرخ مالیاتی'
        verbose_name_plural = 'نرخ‌های مالیاتی'
        ordering = ['-effective_from', 'tax_type']
        indexes = [
            models.Index(fields=['tax_type']),
            models.Index(fields=['effective_from']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.rate}%"


class TaxTransaction(models.Model):
    """تراکنش‌های مالیاتی"""
    
    TRANSACTION_TYPES = [
        ('sale', 'فروش'),
        ('purchase', 'خرید'),
        ('return', 'مرجوعی'),
        ('adjustment', 'تعدیل'),
        ('exemption', 'معافیت'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('submitted', 'ارسال شده'),
        ('accepted', 'پذیرفته شده'),
        ('rejected', 'رد شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    # اطلاعات اصلی
    transaction_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='شماره تراکنش'
    )
    transaction_type = models.CharField(
        max_length=15, 
        choices=TRANSACTION_TYPES, 
        verbose_name='نوع تراکنش'
    )
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name='وضعیت'
    )
    
    # مودی
    taxpayer = models.ForeignKey(
        TaxPayer, 
        on_delete=models.CASCADE, 
        related_name='tax_transactions',
        verbose_name='مودی'
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
    
    # تاریخ‌ها
    transaction_date = models.DateField(default=timezone.now, verbose_name='تاریخ تراکنش')
    due_date = models.DateField(blank=True, null=True, verbose_name='تاریخ سررسید')
    
    # مبالغ
    gross_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ ناخالص'
    )
    tax_exempt_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ معاف'
    )
    taxable_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ مشمول مالیات'
    )
    tax_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ مالیات'
    )
    net_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ خالص'
    )
    
    # اطلاعات اضافی
    description = models.TextField(blank=True, null=True, verbose_name='شرح')
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
    
    class Meta:
        verbose_name = 'تراکنش مالیاتی'
        verbose_name_plural = 'تراکنش‌های مالیاتی'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['taxpayer']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_date']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - {self.taxpayer.customer.full_name}"