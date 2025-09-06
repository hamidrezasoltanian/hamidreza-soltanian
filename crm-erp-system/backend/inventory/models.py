from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from products.models import Product


class Warehouse(models.Model):
    """انبار"""
    
    name = models.CharField(max_length=100, verbose_name='نام انبار')
    code = models.CharField(max_length=20, unique=True, verbose_name='کد انبار')
    address = models.TextField(verbose_name='آدرس')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='تلفن')
    manager = models.CharField(max_length=100, blank=True, null=True, verbose_name='مدیر انبار')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'انبار'
        verbose_name_plural = 'انبارها'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class InventoryItem(models.Model):
    """آیتم موجودی در انبار"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='inventory_items',
        verbose_name='محصول'
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='inventory_items',
        verbose_name='انبار'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مقدار'
    )
    reserved_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مقدار رزرو شده'
    )
    min_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='حداقل موجودی'
    )
    max_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='حداکثر موجودی'
    )
    location = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='مکان در انبار'
    )
    last_updated = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    
    class Meta:
        verbose_name = 'آیتم موجودی'
        verbose_name_plural = 'آیتم‌های موجودی'
        unique_together = ['product', 'warehouse']
        ordering = ['warehouse', 'product']
    
    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}"
    
    @property
    def available_quantity(self):
        """مقدار قابل استفاده"""
        return self.quantity - self.reserved_quantity
    
    @property
    def is_low_stock(self):
        """آیا موجودی کم است؟"""
        return self.available_quantity <= self.min_quantity
    
    @property
    def is_out_of_stock(self):
        """آیا موجودی تمام شده؟"""
        return self.available_quantity <= 0


class LotNumber(models.Model):
    """شماره لات"""
    
    lot_number = models.CharField(max_length=50, unique=True, verbose_name='شماره لات')
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='lots',
        verbose_name='محصول'
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE,
        verbose_name='انبار'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='مقدار'
    )
    production_date = models.DateField(verbose_name='تاریخ تولید')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='تاریخ انقضا')
    supplier = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='تأمین‌کننده'
    )
    batch_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='شماره بچ'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'شماره لات'
        verbose_name_plural = 'شماره‌های لات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lot_number']),
            models.Index(fields=['product']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.lot_number} - {self.product.name}"
    
    @property
    def is_expired(self):
        """آیا منقضی شده؟"""
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False
    
    @property
    def days_to_expiry(self):
        """روزهای باقی‌مانده تا انقضا"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now().date()
            return delta.days
        return None


class StockMovement(models.Model):
    """حرکت موجودی"""
    
    MOVEMENT_TYPES = [
        ('in', 'ورود'),
        ('out', 'خروج'),
        ('transfer', 'انتقال'),
        ('adjustment', 'تعدیل'),
        ('reserve', 'رزرو'),
        ('unreserve', 'لغو رزرو'),
    ]
    
    movement_type = models.CharField(
        max_length=15, 
        choices=MOVEMENT_TYPES, 
        verbose_name='نوع حرکت'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stock_movements',
        verbose_name='محصول'
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='stock_movements',
        verbose_name='انبار'
    )
    lot_number = models.ForeignKey(
        LotNumber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='شماره لات'
    )
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='مقدار'
    )
    unit_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='هزینه واحد'
    )
    total_cost = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='هزینه کل'
    )
    
    # انبار مقصد (برای انتقال)
    destination_warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='incoming_transfers',
        verbose_name='انبار مقصد'
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
    
    # اطلاعات اضافی
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    movement_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ حرکت')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    
    class Meta:
        verbose_name = 'حرکت موجودی'
        verbose_name_plural = 'حرکت‌های موجودی'
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['product']),
            models.Index(fields=['warehouse']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['movement_date']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        """محاسبه هزینه کل"""
        self.total_cost = self.quantity * self.unit_cost
        super().save(*args, **kwargs)


class StockAdjustment(models.Model):
    """تعدیل موجودی"""
    
    ADJUSTMENT_TYPES = [
        ('physical_count', 'شمارش فیزیکی'),
        ('damage', 'آسیب'),
        ('theft', 'سرقت'),
        ('expired', 'منقضی شده'),
        ('other', 'سایر'),
    ]
    
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='adjustments',
        verbose_name='انبار'
    )
    adjustment_type = models.CharField(
        max_length=15, 
        choices=ADJUSTMENT_TYPES, 
        verbose_name='نوع تعدیل'
    )
    reference_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='شماره مرجع'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    status = models.CharField(
        max_length=15, 
        choices=[
            ('draft', 'پیش‌نویس'),
            ('pending', 'در انتظار تأیید'),
            ('approved', 'تأیید شده'),
            ('rejected', 'رد شده'),
        ],
        default='draft',
        verbose_name='وضعیت'
    )
    adjustment_date = models.DateTimeField(default=timezone.now, verbose_name='تاریخ تعدیل')
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
        related_name='approved_adjustments',
        verbose_name='تأیید شده توسط'
    )
    approved_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ تأیید')
    
    class Meta:
        verbose_name = 'تعدیل موجودی'
        verbose_name_plural = 'تعدیل‌های موجودی'
        ordering = ['-adjustment_date']
    
    def __str__(self):
        return f"تعدیل {self.warehouse.name} - {self.reference_number}"


class StockAdjustmentItem(models.Model):
    """آیتم‌های تعدیل موجودی"""
    
    adjustment = models.ForeignKey(
        StockAdjustment, 
        on_delete=models.CASCADE, 
        related_name='items',
        verbose_name='تعدیل'
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name='محصول'
    )
    lot_number = models.ForeignKey(
        LotNumber, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='شماره لات'
    )
    current_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='مقدار فعلی'
    )
    actual_quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='مقدار واقعی'
    )
    difference = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name='تفاوت'
    )
    unit_cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='هزینه واحد'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    
    class Meta:
        verbose_name = 'آیتم تعدیل'
        verbose_name_plural = 'آیتم‌های تعدیل'
        unique_together = ['adjustment', 'product', 'lot_number']
    
    def __str__(self):
        return f"{self.adjustment} - {self.product.name}"
    
    def save(self, *args, **kwargs):
        """محاسبه تفاوت"""
        self.difference = self.actual_quantity - self.current_quantity
        super().save(*args, **kwargs)