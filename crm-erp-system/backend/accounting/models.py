from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class ChartOfAccounts(models.Model):
    """کدینگ حسابداری - مطابق استاندارد ایران"""
    
    ACCOUNT_TYPES = [
        ('asset', 'دارایی'),
        ('liability', 'بدهی'),
        ('equity', 'حقوق صاحبان سهام'),
        ('revenue', 'درآمد'),
        ('expense', 'هزینه'),
    ]
    
    BALANCE_TYPES = [
        ('debit', 'بدهکار'),
        ('credit', 'بستانکار'),
    ]
    
    # کدینگ 4 رقمی مطابق استاندارد ایران
    account_code = models.CharField(
        max_length=10, 
        unique=True, 
        verbose_name='کد حساب'
    )
    parent_account = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='sub_accounts',
        verbose_name='حساب والد'
    )
    account_name = models.CharField(max_length=200, verbose_name='نام حساب')
    account_name_en = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        verbose_name='نام انگلیسی'
    )
    account_type = models.CharField(
        max_length=10, 
        choices=ACCOUNT_TYPES, 
        verbose_name='نوع حساب'
    )
    balance_type = models.CharField(
        max_length=10, 
        choices=BALANCE_TYPES, 
        verbose_name='نوع مانده'
    )
    level = models.PositiveIntegerField(default=1, verbose_name='سطح')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    is_leaf = models.BooleanField(default=True, verbose_name='حساب نهایی')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'کدینگ حسابداری'
        verbose_name_plural = 'کدینگ حسابداری'
        ordering = ['account_code']
        indexes = [
            models.Index(fields=['account_code']),
            models.Index(fields=['account_type']),
            models.Index(fields=['parent_account']),
        ]
    
    def __str__(self):
        return f"{self.account_code} - {self.account_name}"
    
    @property
    def full_path(self):
        """مسیر کامل حساب"""
        path = [f"{self.account_code} - {self.account_name}"]
        current = self.parent_account
        while current:
            path.insert(0, f"{current.account_code} - {current.account_name}")
            current = current.parent_account
        return ' > '.join(path)


class FiscalYear(models.Model):
    """سال مالی"""
    
    name = models.CharField(max_length=50, verbose_name='نام سال مالی')
    start_date = models.DateField(verbose_name='تاریخ شروع')
    end_date = models.DateField(verbose_name='تاریخ پایان')
    is_active = models.BooleanField(default=False, verbose_name='سال فعال')
    is_closed = models.BooleanField(default=False, verbose_name='بسته شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'سال مالی'
        verbose_name_plural = 'سال‌های مالی'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date.year})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date >= self.end_date:
            raise ValidationError('تاریخ شروع باید قبل از تاریخ پایان باشد')


class Journal(models.Model):
    """دفتر روزنامه"""
    
    JOURNAL_TYPES = [
        ('general', 'عمومی'),
        ('sales', 'فروش'),
        ('purchase', 'خرید'),
        ('cash', 'نقدی'),
        ('bank', 'بانکی'),
        ('inventory', 'انبار'),
        ('payroll', 'حقوق و دستمزد'),
        ('adjustment', 'تعدیل'),
    ]
    
    journal_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='شماره سند'
    )
    journal_type = models.CharField(
        max_length=15, 
        choices=JOURNAL_TYPES, 
        default='general',
        verbose_name='نوع سند'
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, 
        on_delete=models.CASCADE, 
        related_name='journals',
        verbose_name='سال مالی'
    )
    date = models.DateField(default=timezone.now, verbose_name='تاریخ سند')
    description = models.TextField(verbose_name='شرح سند')
    total_debit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مجموع بدهکار'
    )
    total_credit = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مجموع بستانکار'
    )
    is_posted = models.BooleanField(default=False, verbose_name='ثبت شده')
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    created_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        verbose_name='ایجاد شده توسط'
    )
    posted_by = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        related_name='posted_journals',
        verbose_name='ثبت شده توسط'
    )
    posted_at = models.DateTimeField(blank=True, null=True, verbose_name='تاریخ ثبت')
    
    class Meta:
        verbose_name = 'دفتر روزنامه'
        verbose_name_plural = 'دفتر روزنامه'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['journal_number']),
            models.Index(fields=['fiscal_year']),
            models.Index(fields=['date']),
            models.Index(fields=['is_posted']),
        ]
    
    def __str__(self):
        return f"{self.journal_number} - {self.description[:50]}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.total_debit != self.total_credit:
            raise ValidationError('مجموع بدهکار و بستانکار باید برابر باشد')


class JournalEntry(models.Model):
    """آیتم‌های دفتر روزنامه"""
    
    journal = models.ForeignKey(
        Journal, 
        on_delete=models.CASCADE, 
        related_name='entries',
        verbose_name='سند'
    )
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.CASCADE, 
        verbose_name='حساب'
    )
    description = models.TextField(verbose_name='شرح')
    debit_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ بدهکار'
    )
    credit_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ بستانکار'
    )
    sort_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        verbose_name = 'آیتم دفتر روزنامه'
        verbose_name_plural = 'آیتم‌های دفتر روزنامه'
        ordering = ['journal', 'sort_order']
    
    def __str__(self):
        return f"{self.journal.journal_number} - {self.account.account_name}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.debit_amount > 0 and self.credit_amount > 0:
            raise ValidationError('هر آیتم باید فقط بدهکار یا بستانکار باشد')
        if self.debit_amount == 0 and self.credit_amount == 0:
            raise ValidationError('مبلغ آیتم نمی‌تواند صفر باشد')


class Ledger(models.Model):
    """دفتر کل"""
    
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.CASCADE, 
        related_name='ledger_entries',
        verbose_name='حساب'
    )
    fiscal_year = models.ForeignKey(
        FiscalYear, 
        on_delete=models.CASCADE, 
        related_name='ledger_entries',
        verbose_name='سال مالی'
    )
    date = models.DateField(verbose_name='تاریخ')
    journal = models.ForeignKey(
        Journal, 
        on_delete=models.CASCADE, 
        verbose_name='سند'
    )
    description = models.TextField(verbose_name='شرح')
    debit_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ بدهکار'
    )
    credit_amount = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مبلغ بستانکار'
    )
    balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        verbose_name='مانده'
    )
    
    class Meta:
        verbose_name = 'دفتر کل'
        verbose_name_plural = 'دفتر کل'
        ordering = ['account', 'date']
        indexes = [
            models.Index(fields=['account']),
            models.Index(fields=['fiscal_year']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.account.account_name} - {self.date}"


class TrialBalance(models.Model):
    """تراز آزمایشی"""
    
    fiscal_year = models.ForeignKey(
        FiscalYear, 
        on_delete=models.CASCADE, 
        related_name='trial_balances',
        verbose_name='سال مالی'
    )
    account = models.ForeignKey(
        ChartOfAccounts, 
        on_delete=models.CASCADE, 
        verbose_name='حساب'
    )
    debit_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مانده بدهکار'
    )
    credit_balance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='مانده بستانکار'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'تراز آزمایشی'
        verbose_name_plural = 'تراز آزمایشی'
        ordering = ['account']
        unique_together = ['fiscal_year', 'account']
    
    def __str__(self):
        return f"{self.fiscal_year.name} - {self.account.account_name}"


class CostCenter(models.Model):
    """مرکز هزینه"""
    
    code = models.CharField(max_length=20, unique=True, verbose_name='کد مرکز هزینه')
    name = models.CharField(max_length=200, verbose_name='نام مرکز هزینه')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='sub_centers',
        verbose_name='مرکز والد'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    description = models.TextField(blank=True, null=True, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'مرکز هزینه'
        verbose_name_plural = 'مراکز هزینه'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class BankAccount(models.Model):
    """حساب بانکی"""
    
    ACCOUNT_TYPES = [
        ('current', 'جاری'),
        ('savings', 'پس‌انداز'),
        ('deposit', 'سپرده'),
        ('credit', 'اعتباری'),
    ]
    
    bank_name = models.CharField(max_length=100, verbose_name='نام بانک')
    branch_name = models.CharField(max_length=100, verbose_name='نام شعبه')
    account_number = models.CharField(max_length=50, verbose_name='شماره حساب')
    account_type = models.CharField(
        max_length=10, 
        choices=ACCOUNT_TYPES, 
        default='current',
        verbose_name='نوع حساب'
    )
    account_holder = models.CharField(max_length=200, verbose_name='صاحب حساب')
    iban = models.CharField(
        max_length=34, 
        blank=True, 
        null=True,
        verbose_name='شماره شبا'
    )
    currency = models.CharField(
        max_length=3, 
        default='IRR',
        verbose_name='واحد پول'
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    notes = models.TextField(blank=True, null=True, verbose_name='یادداشت‌ها')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    
    class Meta:
        verbose_name = 'حساب بانکی'
        verbose_name_plural = 'حساب‌های بانکی'
        ordering = ['bank_name', 'account_number']
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"