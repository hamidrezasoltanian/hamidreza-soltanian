from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from customers.models import Customer, Personnel
from products.models import Product


class Invoice(models.Model):
    """فاکتور"""
    
    INVOICE_TYPES = [
        ('sale', 'فروش'),
        ('return', 'مرجوعی'),
        ('credit', 'اعتباری'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'پیش‌نویس'),
        ('pending_approval', 'در انتظار تأیید'),
        ('approved', 'تأیید شده'),
        ('printed', 'چاپ شده'),
        ('cancelled', 'لغو شده'),
        ('paid', 'پرداخت شده'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('unpaid', 'پرداخت نشده'),
        ('partial', 'پرداخت جزئی'),
        ('paid', 'پرداخت شده'),
        ('overpaid', 'پرداخت اضافی'),
    ]
    
    # اطلاعات اصلی
    invoice_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='شماره فاکتور'
    )
    invoice_type = models.CharField(
        max_length=10, 
        choices=INVOICE_TYPES, 
        default='sale',
        verbose_name='نوع فاکتور'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft',
        verbose_name='وضعیت'
    )
    payment_status = models.CharField(
        max_length=15, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='unpaid',
        verbose_name='وضعیت پرداخت'
    )
    
    # مشتری
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='invoices',
        verbose_name='مشتری'
    )
    contact_person = models.ForeignKey(
        Personnel, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='شخص تماس'
    )
    
    # تاریخ‌ها
    invoice_date = models.DateField(default=timezone.now, verbose_name='تاریخ فاکتور')
    due_date = models.DateField(blank=True, null=True, verbose_name='تاریخ سررسید')
    
    # مبالغ
    subtotal = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='جمع کل'
    )
    discount_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ تخفیف'
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='درصد تخفیف'
    )
    tax_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ مالیات'
    )
    tax_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=9,
        validators=[MinValueValidator(0)],
        verbose_name='درصد مالیات'
    )
    total_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ کل'
    )
    paid_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ پرداخت شده'
    )
    remaining_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name='مبلغ باقی‌مانده'
    )
    
    # اطلاعات اضافی
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    terms_conditions = models.TextField(blank=True, null=True, verbose_name='شرایط و ضوابط')
    
    # اطلاعات سیستم
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    approved_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='approved_invoices',
        verbose_name='تأیید شده توسط'
    )
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تأیید')
    
    class Meta:
        verbose_name = 'فاکتور'
        verbose_name_plural = 'فاکتورها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['customer']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"فاکتور {self.invoice_number} - {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        """محاسبه مبالغ"""
        # محاسبه تخفیف
        if self.discount_percentage > 0:
            self.discount_amount = (self.subtotal * self.discount_percentage) / 100
        
        # محاسبه مالیات
        taxable_amount = self.subtotal - self.discount_amount
        self.tax_amount = (taxable_amount * self.tax_percentage) / 100
        
        # محاسبه مبلغ کل
        self.total_amount = taxable_amount + self.tax_amount
        
        # محاسبه مبلغ باقی‌مانده
        self.remaining_amount = self.total_amount - self.paid_amount
        
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """آیتم‌های فاکتور"""
    
    invoice = models.ForeignKey(
        Invoice, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='فاکتور'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name='محصول'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='مقدار'
    )
    unit_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت واحد'
    )
    discount_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ تخفیف'
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='درصد تخفیف'
    )
    tax_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ مالیات'
    )
    total_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ کل'
    )
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        verbose_name = 'آیتم فاکتور'
        verbose_name_plural = 'آیتم‌های فاکتور'
        ordering = ['invoice', 'sort_order']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """محاسبه مبالغ"""
        # محاسبه تخفیف
        if self.discount_percentage > 0:
            self.discount_amount = (self.quantity * self.unit_price * self.discount_percentage) / 100
        
        # محاسبه مبلغ قبل از مالیات
        before_tax = (self.quantity * self.unit_price) - self.discount_amount
        
        # محاسبه مالیات
        self.tax_amount = (before_tax * self.invoice.tax_percentage) / 100
        
        # محاسبه مبلغ کل
        self.total_amount = before_tax + self.tax_amount
        
        super().save(*args, **kwargs)