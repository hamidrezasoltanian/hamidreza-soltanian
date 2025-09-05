from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class Customer(models.Model):
    """مدل مشتری - شامل اطلاعات کامل مشتری"""
    
    CUSTOMER_TYPES = [
        ('individual', 'حقیقی'),
        ('legal', 'حقوقی'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('suspended', 'معلق'),
    ]
    
    # اطلاعات اصلی
    customer_code = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name='کد مشتری',
        help_text='کد یکتای مشتری'
    )
    customer_type = models.CharField(
        max_length=10, 
        choices=CUSTOMER_TYPES, 
        default='individual',
        verbose_name='نوع مشتری'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='وضعیت'
    )
    
    # اطلاعات شخصی/شرکتی
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name='نام شرکت'
    )
    
    # اطلاعات تماس
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="شماره تلفن باید در فرمت صحیح وارد شود."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        verbose_name='شماره تلفن'
    )
    mobile_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')
    website = models.URLField(blank=True, null=True, verbose_name='وب‌سایت')
    
    # آدرس
    address = models.TextField(verbose_name='آدرس')
    postal_code = models.CharField(
        max_length=10, 
        validators=[RegexValidator(r'^\d{10}$', 'کد پستی باید 10 رقم باشد')],
        verbose_name='کد پستی'
    )
    city = models.CharField(max_length=100, verbose_name='شهر')
    state = models.CharField(max_length=100, verbose_name='استان')
    country = models.CharField(max_length=100, default='ایران', verbose_name='کشور')
    
    # اطلاعات اقتصادی
    economic_code = models.CharField(
        max_length=12, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{12}$', 'کد اقتصادی باید 12 رقم باشد')],
        verbose_name='کد اقتصادی'
    )
    national_id = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{10}$', 'شناسه ملی باید 10 رقم باشد')],
        verbose_name='شناسه ملی'
    )
    registration_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='شماره ثبت'
    )
    
    # اطلاعات مالی
    credit_limit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name='حد اعتبار'
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        verbose_name='درصد تخفیف'
    )
    
    # اطلاعات اضافی
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    tags = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text='تگ‌ها را با کاما جدا کنید',
        verbose_name='تگ‌ها'
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
        verbose_name = 'مشتری'
        verbose_name_plural = 'مشتریان'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_code']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        if self.customer_type == 'legal' and self.company_name:
            return f"{self.company_name} ({self.customer_code})"
        return f"{self.first_name} {self.last_name} ({self.customer_code})"
    
    @property
    def full_name(self):
        """نام کامل مشتری"""
        if self.customer_type == 'legal' and self.company_name:
            return self.company_name
        return f"{self.first_name} {self.last_name}"
    
    def get_tags_list(self):
        """لیست تگ‌ها را برمی‌گرداند"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags_list):
        """تگ‌ها را تنظیم می‌کند"""
        self.tags = ', '.join(tags_list) if tags_list else None


class CustomerCategory(models.Model):
    """دسته‌بندی مشتریان"""
    
    name = models.CharField(max_length=100, unique=True, verbose_name='نام دسته')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    color = models.CharField(
        max_length=7, 
        default='#007bff',
        help_text='رنگ دسته (کد هگز)',
        verbose_name='رنگ'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'دسته مشتری'
        verbose_name_plural = 'دسته‌های مشتری'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerCategoryMembership(models.Model):
    """عضویت مشتری در دسته‌ها"""
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='category_memberships',
        verbose_name='مشتری'
    )
    category = models.ForeignKey(
        CustomerCategory, 
        on_delete=models.CASCADE,
        verbose_name='دسته'
    )
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ انتساب')
    assigned_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='انتساب شده توسط'
    )
    
    class Meta:
        verbose_name = 'عضویت در دسته'
        verbose_name_plural = 'عضویت‌های دسته'
        unique_together = ['customer', 'category']
    
    def __str__(self):
        return f"{self.customer} - {self.category}"