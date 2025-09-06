from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from customers.models import Customer


class Personnel(models.Model):
    """مدل پرسنل - کارمندان مشتریان"""
    
    GENDER_CHOICES = [
        ('male', 'مرد'),
        ('female', 'زن'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'مجرد'),
        ('married', 'متأهل'),
        ('divorced', 'مطلقه'),
        ('widowed', 'بیوه'),
    ]
    
    # ارتباط با مشتری
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='personnel',
        verbose_name='مشتری'
    )
    
    # اطلاعات شخصی
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    father_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='نام پدر'
    )
    national_id = models.CharField(
        max_length=10, 
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'کد ملی باید 10 رقم باشد')],
        verbose_name='کد ملی'
    )
    birth_date = models.DateField(blank=True, null=True, verbose_name='تاریخ تولد')
    gender = models.CharField(
        max_length=6, 
        choices=GENDER_CHOICES, 
        blank=True, 
        null=True,
        verbose_name='جنسیت'
    )
    marital_status = models.CharField(
        max_length=10, 
        choices=MARITAL_STATUS_CHOICES, 
        blank=True, 
        null=True,
        verbose_name='وضعیت تأهل'
    )
    
    # اطلاعات تماس
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="شماره تلفن باید در فرمت صحیح وارد شود."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True,
        verbose_name='شماره تلفن'
    )
    mobile_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        verbose_name='شماره موبایل'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='ایمیل')
    
    # آدرس
    address = models.TextField(blank=True, null=True, verbose_name='آدرس')
    postal_code = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{10}$', 'کد پستی باید 10 رقم باشد')],
        verbose_name='کد پستی'
    )
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='شهر')
    
    # اطلاعات شغلی
    position = models.CharField(max_length=100, verbose_name='سمت')
    department = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='بخش'
    )
    employee_id = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        verbose_name='شماره پرسنلی'
    )
    hire_date = models.DateField(blank=True, null=True, verbose_name='تاریخ استخدام')
    salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        verbose_name='حقوق'
    )
    
    # اطلاعات اضافی
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    is_primary_contact = models.BooleanField(
        default=False, 
        verbose_name='تماس اصلی',
        help_text='آیا این شخص تماس اصلی مشتری است؟'
    )
    is_authorized_for_orders = models.BooleanField(
        default=False, 
        verbose_name='مجاز برای سفارش',
        help_text='آیا این شخص مجاز به ثبت سفارش است؟'
    )
    is_authorized_for_payment = models.BooleanField(
        default=False, 
        verbose_name='مجاز برای پرداخت',
        help_text='آیا این شخص مجاز به تأیید پرداخت است؟'
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
        verbose_name = 'پرسنل'
        verbose_name_plural = 'پرسنل'
        ordering = ['customer', 'last_name', 'first_name']
        indexes = [
            models.Index(fields=['customer']),
            models.Index(fields=['national_id']),
            models.Index(fields=['mobile_number']),
            models.Index(fields=['position']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.customer.company_name or self.customer.full_name}"
    
    @property
    def full_name(self):
        """نام کامل پرسنل"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """سن پرسنل"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class PersonnelDocument(models.Model):
    """اسناد و مدارک پرسنل"""
    
    DOCUMENT_TYPES = [
        ('id_card', 'کارت ملی'),
        ('birth_certificate', 'شناسنامه'),
        ('passport', 'پاسپورت'),
        ('contract', 'قرارداد'),
        ('other', 'سایر'),
    ]
    
    personnel = models.ForeignKey(
        Personnel, 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name='پرسنل'
    )
    document_type = models.CharField(
        max_length=20, 
        choices=DOCUMENT_TYPES, 
        verbose_name='نوع سند'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان سند')
    file = models.FileField(upload_to='personnel_documents/', verbose_name='فایل')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    uploaded_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='آپلود شده توسط'
    )
    
    class Meta:
        verbose_name = 'سند پرسنل'
        verbose_name_plural = 'اسناد پرسنل'
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.personnel} - {self.title}"


class PersonnelContact(models.Model):
    """اطلاعات تماس اضافی پرسنل"""
    
    CONTACT_TYPES = [
        ('phone', 'تلفن'),
        ('mobile', 'موبایل'),
        ('email', 'ایمیل'),
        ('fax', 'فکس'),
        ('whatsapp', 'واتساپ'),
        ('telegram', 'تلگرام'),
        ('other', 'سایر'),
    ]
    
    personnel = models.ForeignKey(
        Personnel, 
        on_delete=models.CASCADE, 
        related_name='contacts',
        verbose_name='پرسنل'
    )
    contact_type = models.CharField(
        max_length=10, 
        choices=CONTACT_TYPES, 
        verbose_name='نوع تماس'
    )
    value = models.CharField(max_length=200, verbose_name='مقدار')
    is_primary = models.BooleanField(default=False, verbose_name='اصلی')
    notes = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='یادداشت'
    )
    
    class Meta:
        verbose_name = 'تماس پرسنل'
        verbose_name_plural = 'تماس‌های پرسنل'
        ordering = ['personnel', 'contact_type']
    
    def __str__(self):
        return f"{self.personnel} - {self.get_contact_type_display()}: {self.value}"