"""
Management command to seed the database with initial test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random
from decimal import Decimal

from customers.models import Customer, CustomerCategory
from products.models import Product, ProductCategory
from inventory.models import Warehouse, InventoryLocation, StockItem
from invoices.models import Invoice, InvoiceItem, Payment
from crm.models import Lead
from accounting.models import ChartOfAccounts, CostCenter
from tax_system.models import TaxPayer, TaxRate
from personnel.models import Personnel, Department, Position


class Command(BaseCommand):
    help = 'Seeds the database with initial test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Starting to seed database...')
        
        with transaction.atomic():
            # Create superuser
            self.create_superuser()
            
            # Create groups and permissions
            self.create_groups()
            
            # Create basic data
            self.create_departments_positions()
            self.create_customer_categories()
            self.create_product_categories()
            self.create_warehouses()
            self.create_cost_centers()
            self.create_chart_of_accounts()
            self.create_tax_rates()
            
            # Create main data
            self.create_personnel()
            self.create_customers()
            self.create_products()
            self.create_stock_items()
            self.create_leads()
            self.create_invoices()
            self.create_tax_payers()
            
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))

    def create_superuser(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@crm-erp.com',
                password='admin123',
                first_name='مدیر',
                last_name='سیستم'
            )
            self.stdout.write('  ✓ Superuser created (username: admin, password: admin123)')

    def create_groups(self):
        groups = [
            'مدیران',
            'حسابداران',
            'فروشندگان',
            'انبارداران',
            'کارمندان'
        ]
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write('  ✓ User groups created')

    def create_departments_positions(self):
        departments = [
            {'name': 'مدیریت', 'code': 'MGT'},
            {'name': 'فروش', 'code': 'SLS'},
            {'name': 'حسابداری', 'code': 'ACC'},
            {'name': 'انبار', 'code': 'WRH'},
            {'name': 'پشتیبانی', 'code': 'SUP'},
        ]
        
        for dept_data in departments:
            Department.objects.get_or_create(**dept_data)
        
        positions = [
            {'title': 'مدیرعامل', 'level': 1},
            {'title': 'مدیر فروش', 'level': 2},
            {'title': 'مدیر مالی', 'level': 2},
            {'title': 'کارشناس فروش', 'level': 3},
            {'title': 'حسابدار', 'level': 3},
            {'title': 'انباردار', 'level': 3},
        ]
        
        for pos_data in positions:
            Position.objects.get_or_create(**pos_data)
        
        self.stdout.write('  ✓ Departments and positions created')

    def create_customer_categories(self):
        categories = [
            {'name': 'عمده فروش', 'code': 'WHOLESALE'},
            {'name': 'خرده فروش', 'code': 'RETAIL'},
            {'name': 'شرکتی', 'code': 'CORPORATE'},
            {'name': 'VIP', 'code': 'VIP'},
        ]
        for cat in categories:
            CustomerCategory.objects.get_or_create(**cat)
        self.stdout.write('  ✓ Customer categories created')

    def create_product_categories(self):
        categories = [
            {'name': 'الکترونیک', 'code': 'ELEC', 'description': 'محصولات الکترونیکی'},
            {'name': 'لوازم خانگی', 'code': 'HOME', 'description': 'لوازم خانگی'},
            {'name': 'پوشاک', 'code': 'CLOTH', 'description': 'پوشاک و البسه'},
            {'name': 'مواد غذایی', 'code': 'FOOD', 'description': 'مواد غذایی و خوراکی'},
        ]
        for cat in categories:
            ProductCategory.objects.get_or_create(**cat)
        self.stdout.write('  ✓ Product categories created')

    def create_warehouses(self):
        warehouses = [
            {
                'name': 'انبار مرکزی',
                'code': 'MAIN',
                'address': 'تهران، خیابان ولیعصر',
                'phone': '02112345678',
                'is_active': True
            },
            {
                'name': 'انبار شعبه شمال',
                'code': 'NORTH',
                'address': 'تهران، تجریش',
                'phone': '02122345678',
                'is_active': True
            }
        ]
        
        for wh_data in warehouses:
            warehouse, created = Warehouse.objects.get_or_create(**wh_data)
            if created:
                # Create locations for each warehouse
                locations = ['A1', 'A2', 'B1', 'B2', 'C1']
                for loc_code in locations:
                    InventoryLocation.objects.create(
                        warehouse=warehouse,
                        code=f"{warehouse.code}-{loc_code}",
                        name=f"موقعیت {loc_code}",
                        aisle=loc_code[0],
                        shelf=loc_code[1]
                    )
        
        self.stdout.write('  ✓ Warehouses and locations created')

    def create_cost_centers(self):
        centers = [
            {'code': 'CC001', 'name': 'مرکز هزینه فروش'},
            {'code': 'CC002', 'name': 'مرکز هزینه اداری'},
            {'code': 'CC003', 'name': 'مرکز هزینه تولید'},
        ]
        for center in centers:
            CostCenter.objects.get_or_create(**center)
        self.stdout.write('  ✓ Cost centers created')

    def create_chart_of_accounts(self):
        accounts = [
            # دارایی‌ها (Assets) - کد 1
            {'code': '1000', 'name': 'دارایی‌ها', 'account_type': 'asset', 'level': 1},
            {'code': '1100', 'name': 'دارایی‌های جاری', 'account_type': 'asset', 'parent_code': '1000', 'level': 2},
            {'code': '1110', 'name': 'موجودی نقد', 'account_type': 'asset', 'parent_code': '1100', 'level': 3},
            {'code': '1120', 'name': 'حساب‌های بانکی', 'account_type': 'asset', 'parent_code': '1100', 'level': 3},
            {'code': '1130', 'name': 'حساب‌های دریافتنی', 'account_type': 'asset', 'parent_code': '1100', 'level': 3},
            {'code': '1140', 'name': 'موجودی کالا', 'account_type': 'asset', 'parent_code': '1100', 'level': 3},
            
            # بدهی‌ها (Liabilities) - کد 2
            {'code': '2000', 'name': 'بدهی‌ها', 'account_type': 'liability', 'level': 1},
            {'code': '2100', 'name': 'بدهی‌های جاری', 'account_type': 'liability', 'parent_code': '2000', 'level': 2},
            {'code': '2110', 'name': 'حساب‌های پرداختنی', 'account_type': 'liability', 'parent_code': '2100', 'level': 3},
            {'code': '2120', 'name': 'مالیات پرداختنی', 'account_type': 'liability', 'parent_code': '2100', 'level': 3},
            
            # حقوق صاحبان سهام (Equity) - کد 3
            {'code': '3000', 'name': 'حقوق صاحبان سهام', 'account_type': 'equity', 'level': 1},
            {'code': '3100', 'name': 'سرمایه', 'account_type': 'equity', 'parent_code': '3000', 'level': 2},
            {'code': '3200', 'name': 'سود انباشته', 'account_type': 'equity', 'parent_code': '3000', 'level': 2},
            
            # درآمدها (Revenue) - کد 4
            {'code': '4000', 'name': 'درآمدها', 'account_type': 'revenue', 'level': 1},
            {'code': '4100', 'name': 'درآمد فروش', 'account_type': 'revenue', 'parent_code': '4000', 'level': 2},
            {'code': '4200', 'name': 'سایر درآمدها', 'account_type': 'revenue', 'parent_code': '4000', 'level': 2},
            
            # هزینه‌ها (Expenses) - کد 5
            {'code': '5000', 'name': 'هزینه‌ها', 'account_type': 'expense', 'level': 1},
            {'code': '5100', 'name': 'بهای تمام شده کالای فروخته شده', 'account_type': 'expense', 'parent_code': '5000', 'level': 2},
            {'code': '5200', 'name': 'هزینه‌های اداری', 'account_type': 'expense', 'parent_code': '5000', 'level': 2},
            {'code': '5300', 'name': 'هزینه‌های فروش', 'account_type': 'expense', 'parent_code': '5000', 'level': 2},
        ]
        
        # First create parent accounts
        parent_map = {}
        for acc_data in accounts:
            parent_code = acc_data.pop('parent_code', None)
            if parent_code:
                acc_data['parent'] = parent_map.get(parent_code)
            account, _ = ChartOfAccounts.objects.get_or_create(
                code=acc_data['code'],
                defaults=acc_data
            )
            parent_map[account.code] = account
        
        self.stdout.write('  ✓ Chart of accounts created')

    def create_tax_rates(self):
        rates = [
            {'name': 'مالیات بر ارزش افزوده', 'rate': Decimal('0.09'), 'is_active': True},
            {'name': 'عوارض شهرداری', 'rate': Decimal('0.01'), 'is_active': True},
        ]
        for rate in rates:
            TaxRate.objects.get_or_create(**rate)
        self.stdout.write('  ✓ Tax rates created')

    def create_personnel(self):
        dept_sales = Department.objects.get(code='SLS')
        dept_acc = Department.objects.get(code='ACC')
        pos_sales = Position.objects.get(title='کارشناس فروش')
        pos_acc = Position.objects.get(title='حسابدار')
        
        personnel_data = [
            {
                'personnel_code': 'P001',
                'first_name': 'علی',
                'last_name': 'احمدی',
                'national_code': '0012345678',
                'department': dept_sales,
                'position': pos_sales,
                'mobile': '09121234567',
                'email': 'ali.ahmadi@company.com',
                'hire_date': timezone.now().date() - timedelta(days=365),
                'is_active': True
            },
            {
                'personnel_code': 'P002',
                'first_name': 'زهرا',
                'last_name': 'محمدی',
                'national_code': '0023456789',
                'department': dept_acc,
                'position': pos_acc,
                'mobile': '09122345678',
                'email': 'zahra.mohammadi@company.com',
                'hire_date': timezone.now().date() - timedelta(days=200),
                'is_active': True
            }
        ]
        
        for data in personnel_data:
            Personnel.objects.get_or_create(
                personnel_code=data['personnel_code'],
                defaults=data
            )
        self.stdout.write('  ✓ Personnel created')

    def create_customers(self):
        categories = CustomerCategory.objects.all()
        
        customers_data = [
            {
                'customer_code': 'C001',
                'customer_type': 'legal',
                'company_name': 'شرکت نوآوران',
                'national_id': '14007654321',
                'economic_code': '411234567890',
                'registration_number': '123456',
                'phone': '02188776655',
                'mobile': '09121234567',
                'email': 'info@navaran.com',
                'address': 'تهران، خیابان ولیعصر، پلاک 100',
                'postal_code': '1234567890',
                'credit_limit': Decimal('100000000'),
                'is_active': True
            },
            {
                'customer_code': 'C002',
                'customer_type': 'individual',
                'first_name': 'محمد',
                'last_name': 'رضایی',
                'national_id': '0012345678',
                'mobile': '09123456789',
                'email': 'mohammad.rezaei@gmail.com',
                'address': 'تهران، سعادت آباد',
                'credit_limit': Decimal('50000000'),
                'is_active': True
            },
            {
                'customer_code': 'C003',
                'customer_type': 'legal',
                'company_name': 'فروشگاه زنجیره‌ای رفاه',
                'national_id': '14008765432',
                'economic_code': '411345678901',
                'phone': '02144556677',
                'mobile': '09351234567',
                'email': 'info@refah.com',
                'address': 'تهران، میدان ونک',
                'credit_limit': Decimal('200000000'),
                'is_active': True
            }
        ]
        
        for i, data in enumerate(customers_data):
            customer, created = Customer.objects.get_or_create(
                national_id=data['national_id'],
                defaults=data
            )
            if created and categories.exists():
                customer.category = random.choice(categories)
                customer.save()
        
        self.stdout.write('  ✓ Customers created')

    def create_products(self):
        categories = ProductCategory.objects.all()
        
        products_data = [
            {
                'name': 'لپ تاپ ASUS VivoBook',
                'code': 'LAP001',
                'barcode': '6260000010001',
                'unit': 'دستگاه',
                'purchase_price': Decimal('25000000'),
                'sale_price': Decimal('32000000'),
                'min_stock': 5,
                'max_stock': 50,
                'description': 'لپ تاپ ایسوس با پردازنده Core i5',
                'is_active': True
            },
            {
                'name': 'موبایل Samsung Galaxy A54',
                'code': 'MOB001',
                'barcode': '6260000020001',
                'unit': 'دستگاه',
                'purchase_price': Decimal('15000000'),
                'sale_price': Decimal('18000000'),
                'min_stock': 10,
                'max_stock': 100,
                'description': 'گوشی موبایل سامسونگ',
                'is_active': True
            },
            {
                'name': 'یخچال فریزر سامسونگ',
                'code': 'REF001',
                'barcode': '6260000030001',
                'unit': 'دستگاه',
                'purchase_price': Decimal('45000000'),
                'sale_price': Decimal('55000000'),
                'min_stock': 2,
                'max_stock': 20,
                'description': 'یخچال فریزر دو درب',
                'is_active': True
            },
            {
                'name': 'ماشین لباسشویی LG',
                'code': 'WAS001',
                'barcode': '6260000040001',
                'unit': 'دستگاه',
                'purchase_price': Decimal('35000000'),
                'sale_price': Decimal('42000000'),
                'min_stock': 3,
                'max_stock': 30,
                'description': 'ماشین لباسشویی 8 کیلویی',
                'is_active': True
            }
        ]
        
        for data in products_data:
            product, created = Product.objects.get_or_create(
                code=data['code'],
                defaults=data
            )
            if created and categories.exists():
                product.category = random.choice(categories)
                product.save()
        
        self.stdout.write('  ✓ Products created')

    def create_stock_items(self):
        products = Product.objects.all()
        warehouses = Warehouse.objects.all()
        
        for product in products:
            for warehouse in warehouses:
                location = warehouse.locations.first()
                if location:
                    StockItem.objects.get_or_create(
                        product=product,
                        warehouse=warehouse,
                        location=location,
                        defaults={
                            'quantity': random.randint(10, 100),
                            'reserved_quantity': random.randint(0, 10),
                        }
                    )
        
        self.stdout.write('  ✓ Stock items created')

    def create_leads(self):
        personnel = Personnel.objects.first()
        
        leads_data = [
            {
                'title': 'فرصت فروش لپ تاپ به شرکت آریا',
                'company_name': 'شرکت آریا',
                'contact_name': 'مهندس کریمی',
                'phone': '02166778899',
                'mobile': '09121112233',
                'email': 'karimi@aria.com',
                'source': 'website',
                'status': 'qualified',
                'estimated_value': Decimal('150000000'),
                'probability': 70,
                'description': 'نیاز به 5 دستگاه لپ تاپ برای دفتر مرکزی'
            },
            {
                'title': 'فروش لوازم خانگی به فروشگاه پارس',
                'company_name': 'فروشگاه پارس',
                'contact_name': 'آقای احمدی',
                'mobile': '09352223344',
                'source': 'referral',
                'status': 'proposal',
                'estimated_value': Decimal('500000000'),
                'probability': 50,
                'description': 'درخواست قیمت برای تجهیز شعبه جدید'
            }
        ]
        
        for data in leads_data:
            if personnel:
                data['assigned_to'] = personnel
            Lead.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
        
        self.stdout.write('  ✓ Leads created')

    def create_invoices(self):
        customers = Customer.objects.all()
        products = Product.objects.all()
        personnel = Personnel.objects.first()
        
        if not customers.exists() or not products.exists():
            return
        
        for i in range(5):
            customer = random.choice(customers)
            invoice = Invoice.objects.create(
                invoice_number=f'INV-{1001 + i}',
                customer=customer,
                invoice_date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
                due_date=timezone.now().date() + timedelta(days=30),
                status='approved',
                payment_method='cash',
                salesperson=personnel,
                discount_percentage=Decimal('5'),
                notes='فاکتور تست'
            )
            
            # Add items
            for product in random.sample(list(products), min(3, len(products))):
                InvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=random.randint(1, 5),
                    unit_price=product.sale_price,
                    discount_percentage=Decimal('0'),
                    tax_rate=Decimal('9'),
                    description=f'فروش {product.name}'
                )
            
            invoice.calculate_totals()
        
        self.stdout.write('  ✓ Invoices created')

    def create_tax_payers(self):
        customers = Customer.objects.filter(customer_type='legal')
        
        for customer in customers[:2]:
            TaxPayer.objects.get_or_create(
                customer=customer,
                defaults={
                    'tax_file_number': f'TF{random.randint(10000, 99999)}',
                    'vat_registration_number': f'VAT{random.randint(10000, 99999)}',
                    'tax_office_code': '1234',
                    'is_vat_registered': True,
                    'registration_date': timezone.now().date() - timedelta(days=100)
                }
            )
        
        self.stdout.write('  ✓ Tax payers created')