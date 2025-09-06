from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class ProductCategory(models.Model):
    """دسته‌بندی محصولات - ساختار درختی"""
    
    name = models.CharField(max_length=100, verbose_name='نام دسته')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children',
        verbose_name='دسته والد'
    )
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    image = models.ImageField(
        upload_to='product_categories/', 
        blank=True, 
        null=True,
        verbose_name='تصویر'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'دسته محصول'
        verbose_name_plural = 'دسته‌های محصول'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name
    
    @property
    def full_path(self):
        """مسیر کامل دسته"""
        path = [self.name]
        current = self.parent
        while current:
            path.insert(0, current.name)
            current = current.parent
        return ' > '.join(path)


class Product(models.Model):
    """مدل محصول"""
    
    UNIT_TYPES = [
        ('piece', 'عدد'),
        ('kg', 'کیلوگرم'),
        ('gram', 'گرم'),
        ('liter', 'لیتر'),
        ('meter', 'متر'),
        ('box', 'جعبه'),
        ('pack', 'بسته'),
        ('set', 'ست'),
        ('other', 'سایر'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'فعال'),
        ('inactive', 'غیرفعال'),
        ('discontinued', 'متوقف شده'),
        ('draft', 'پیش‌نویس'),
    ]
    
    # اطلاعات اصلی
    product_code = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='کد محصول'
    )
    barcode = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        unique=True,
        verbose_name='بارکد'
    )
    name = models.CharField(max_length=200, verbose_name='نام محصول')
    name_en = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='نام انگلیسی'
    )
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    short_description = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        verbose_name='توضیحات کوتاه'
    )
    
    # دسته‌بندی
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='products',
        verbose_name='دسته'
    )
    
    # واحدها
    base_unit = models.CharField(
        max_length=10, 
        choices=UNIT_TYPES, 
        default='piece',
        verbose_name='واحد پایه'
    )
    purchase_unit = models.CharField(
        max_length=10, 
        choices=UNIT_TYPES, 
        default='piece',
        verbose_name='واحد خرید'
    )
    sale_unit = models.CharField(
        max_length=10, 
        choices=UNIT_TYPES, 
        default='piece',
        verbose_name='واحد فروش'
    )
    
    # تبدیل واحدها
    purchase_to_base_ratio = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=1,
        validators=[MinValueValidator(0.0001)],
        verbose_name='نسبت خرید به پایه'
    )
    sale_to_base_ratio = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=1,
        validators=[MinValueValidator(0.0001)],
        verbose_name='نسبت فروش به پایه'
    )
    
    # قیمت‌ها
    cost_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت تمام شده'
    )
    sale_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت فروش'
    )
    wholesale_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='قیمت عمده'
    )
    
    # موجودی
    min_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='حداقل موجودی'
    )
    max_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='حداکثر موجودی'
    )
    current_stock = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0,
        verbose_name='موجودی فعلی'
    )
    
    # مالیات و تخفیف
    tax_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='نرخ مالیات (%)'
    )
    discount_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='نرخ تخفیف (%)'
    )
    
    # وضعیت
    status = models.CharField(
        max_length=15, 
        choices=STATUS_CHOICES, 
        default='active',
        verbose_name='وضعیت'
    )
    is_service = models.BooleanField(default=False, verbose_name='خدمات')
    is_digital = models.BooleanField(default=False, verbose_name='محصول دیجیتال')
    
    # وزن و ابعاد
    weight = models.DecimalField(
        max_digits=8, 
        decimal_places=3, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='وزن (کیلوگرم)'
    )
    length = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='طول (سانتی‌متر)'
    )
    width = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='عرض (سانتی‌متر)'
    )
    height = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0)],
        verbose_name='ارتفاع (سانتی‌متر)'
    )
    
    # اطلاعات اضافی
    tags = models.CharField(
        max_length=500, 
        blank=True, 
        null=True,
        help_text='تگ‌ها را با کاما جدا کنید',
        verbose_name='تگ‌ها'
    )
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
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['barcode']),
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.product_code})"
    
    def get_tags_list(self):
        """لیست تگ‌ها را برمی‌گرداند"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags(self, tags_list):
        """تگ‌ها را تنظیم می‌کند"""
        self.tags = ', '.join(tags_list) if tags_list else None
    
    @property
    def is_low_stock(self):
        """آیا موجودی کم است؟"""
        return self.current_stock <= self.min_stock
    
    @property
    def is_out_of_stock(self):
        """آیا موجودی تمام شده؟"""
        return self.current_stock <= 0


class ProductImage(models.Model):
    """تصاویر محصول"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images',
        verbose_name='محصول'
    )
    image = models.ImageField(upload_to='product_images/', verbose_name='تصویر')
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name='عنوان')
    alt_text = models.CharField(max_length=200, blank=True, null=True, verbose_name='متن جایگزین')
    is_primary = models.BooleanField(default=False, verbose_name='تصویر اصلی')
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصول'
        ordering = ['product', 'sort_order']
    
    def __str__(self):
        return f"{self.product.name} - {self.title or 'تصویر'}"


class ProductAttribute(models.Model):
    """ویژگی‌های محصول"""
    
    ATTRIBUTE_TYPES = [
        ('text', 'متن'),
        ('number', 'عدد'),
        ('boolean', 'بله/خیر'),
        ('choice', 'انتخابی'),
        ('date', 'تاریخ'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='نام ویژگی')
    attribute_type = models.CharField(
        max_length=10, 
        choices=ATTRIBUTE_TYPES, 
        default='text',
        verbose_name='نوع ویژگی'
    )
    is_required = models.BooleanField(default=False, verbose_name='اجباری')
    is_filterable = models.BooleanField(default=False, verbose_name='قابل فیلتر')
    choices = models.TextField(
        blank=True, 
        null=True,
        help_text='برای نوع انتخابی، گزینه‌ها را در هر خط بنویسید',
        verbose_name='گزینه‌ها'
    )
    unit = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        verbose_name='واحد'
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        verbose_name = 'ویژگی محصول'
        verbose_name_plural = 'ویژگی‌های محصول'
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_choices_list(self):
        """لیست گزینه‌ها را برمی‌گرداند"""
        if self.attribute_type == 'choice' and self.choices:
            return [choice.strip() for choice in self.choices.split('\n') if choice.strip()]
        return []


class ProductAttributeValue(models.Model):
    """مقادیر ویژگی‌های محصول"""
    
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='attribute_values',
        verbose_name='محصول'
    )
    attribute = models.ForeignKey(
        ProductAttribute, 
        on_delete=models.CASCADE,
        verbose_name='ویژگی'
    )
    value_text = models.TextField(blank=True, null=True, verbose_name='مقدار متنی')
    value_number = models.DecimalField(
        max_digits=15, 
        decimal_places=4, 
        blank=True, 
        null=True,
        verbose_name='مقدار عددی'
    )
    value_boolean = models.BooleanField(blank=True, null=True, verbose_name='مقدار بولی')
    value_date = models.DateField(blank=True, null=True, verbose_name='مقدار تاریخ')
    
    class Meta:
        verbose_name = 'مقدار ویژگی'
        verbose_name_plural = 'مقادیر ویژگی‌ها'
        unique_together = ['product', 'attribute']
    
    def __str__(self):
        return f"{self.product.name} - {self.attribute.name}"
    
    @property
    def value(self):
        """مقدار بر اساس نوع ویژگی"""
        if self.attribute.attribute_type == 'text':
            return self.value_text
        elif self.attribute.attribute_type == 'number':
            return self.value_number
        elif self.attribute.attribute_type == 'boolean':
            return self.value_boolean
        elif self.attribute.attribute_type == 'choice':
            return self.value_text
        elif self.attribute.attribute_type == 'date':
            return self.value_date
        return None