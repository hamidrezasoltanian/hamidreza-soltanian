"""
Initialize database with basic data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal

from customers.models import Customer, CustomerCategory
from products.models import Product, ProductCategory


class Command(BaseCommand):
    help = 'Initialize database with basic data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🚀 Initializing database...\n')
        
        with transaction.atomic():
            # Create superuser
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@crm-erp.com',
                    password='admin123',
                    first_name='مدیر',
                    last_name='سیستم'
                )
                self.stdout.write(self.style.SUCCESS('✓ Admin user created'))
                self.stdout.write('  Username: admin')
                self.stdout.write('  Password: admin123\n')
            else:
                self.stdout.write('✓ Admin user already exists\n')
            
            # Create customer categories
            self.stdout.write('Creating customer categories...')
            categories = [
                {'name': 'عمده فروش', 'color': '#28a745'},
                {'name': 'خرده فروش', 'color': '#17a2b8'},
                {'name': 'شرکتی', 'color': '#007bff'},
            ]
            for cat in categories:
                obj, created = CustomerCategory.objects.get_or_create(
                    name=cat['name'],
                    defaults=cat
                )
                if created:
                    self.stdout.write(f'  + {cat["name"]}')
            
            # Create product categories
            self.stdout.write('\nCreating product categories...')
            prod_categories = [
                {'name': 'الکترونیک', 'description': 'محصولات الکترونیکی'},
                {'name': 'لوازم خانگی', 'description': 'لوازم خانگی برقی'},
                {'name': 'موبایل و تبلت', 'description': 'گوشی موبایل و تبلت'},
            ]
            for cat in prod_categories:
                obj, created = ProductCategory.objects.get_or_create(
                    name=cat['name'],
                    defaults=cat
                )
                if created:
                    self.stdout.write(f'  + {cat["name"]}')
            
            # Create sample customers
            self.stdout.write('\nCreating sample customers...')
            customers = [
                {
                    'customer_code': 'C001',
                    'customer_type': 'legal',
                    'first_name': 'شرکت',
                    'last_name': 'نوآوران',
                    'company_name': 'شرکت نوآوران',
                    'national_id': '14007654321',
                    'economic_code': '411234567890',
                    'phone_number': '02188776655',
                    'mobile_number': '09121234567',
                    'email': 'info@navaran.com',
                    'address': 'تهران، خیابان ولیعصر، پلاک 100',
                    'city': 'تهران',
                    'state': 'تهران',
                    'postal_code': '1234567890',
                    'credit_limit': Decimal('100000000'),
                    'status': 'active'
                },
                {
                    'customer_code': 'C002',
                    'customer_type': 'individual',
                    'first_name': 'محمد',
                    'last_name': 'رضایی',
                    'national_id': '0012345678',
                    'mobile_number': '09123456789',
                    'email': 'mohammad@gmail.com',
                    'address': 'تهران، سعادت آباد',
                    'city': 'تهران',
                    'state': 'تهران',
                    'credit_limit': Decimal('50000000'),
                    'status': 'active'
                },
                {
                    'customer_code': 'C003',
                    'customer_type': 'legal',
                    'first_name': 'فروشگاه',
                    'last_name': 'رفاه',
                    'company_name': 'فروشگاه زنجیره‌ای رفاه',
                    'national_id': '14008765432',
                    'economic_code': '411345678901',
                    'phone_number': '02144556677',
                    'mobile_number': '09351234567',
                    'email': 'info@refah.com',
                    'address': 'تهران، میدان ونک',
                    'city': 'تهران',
                    'state': 'تهران',
                    'credit_limit': Decimal('200000000'),
                    'status': 'active'
                },
            ]
            
            for cust_data in customers:
                obj, created = Customer.objects.get_or_create(
                    customer_code=cust_data['customer_code'],
                    defaults=cust_data
                )
                if created:
                    name = cust_data.get('company_name') or f"{cust_data['first_name']} {cust_data['last_name']}"
                    self.stdout.write(f'  + {name}')
            
            # Create sample products
            self.stdout.write('\nCreating sample products...')
            elec_cat = ProductCategory.objects.get(name='الکترونیک')
            home_cat = ProductCategory.objects.get(name='لوازم خانگی')
            mobile_cat = ProductCategory.objects.get(name='موبایل و تبلت')
            
            products = [
                {
                    'product_code': 'LAP001',
                    'name': 'لپ تاپ ASUS VivoBook 15',
                    'barcode': '6260000010001',
                    'base_unit': 'دستگاه',
                    'cost_price': Decimal('25000000'),
                    'sale_price': Decimal('32000000'),
                    'min_stock': 5,
                    'max_stock': 50,
                    'description': 'لپ تاپ ایسوس با پردازنده Core i5 نسل 11',
                    'status': 'active',
                    'category': elec_cat
                },
                {
                    'product_code': 'MOB001',
                    'name': 'گوشی Samsung Galaxy A54',
                    'barcode': '6260000020001',
                    'base_unit': 'دستگاه',
                    'cost_price': Decimal('15000000'),
                    'sale_price': Decimal('18000000'),
                    'min_stock': 10,
                    'max_stock': 100,
                    'description': 'گوشی موبایل سامسونگ گلکسی A54 با حافظه 256 گیگ',
                    'status': 'active',
                    'category': mobile_cat
                },
                {
                    'product_code': 'REF001',
                    'name': 'یخچال فریزر سامسونگ RT50',
                    'barcode': '6260000030001',
                    'base_unit': 'دستگاه',
                    'cost_price': Decimal('45000000'),
                    'sale_price': Decimal('55000000'),
                    'min_stock': 2,
                    'max_stock': 20,
                    'description': 'یخچال فریزر دو درب سامسونگ با حجم 500 لیتر',
                    'status': 'active',
                    'category': home_cat
                },
                {
                    'product_code': 'WAS001',
                    'name': 'ماشین لباسشویی LG 8kg',
                    'barcode': '6260000040001',
                    'base_unit': 'دستگاه',
                    'cost_price': Decimal('35000000'),
                    'sale_price': Decimal('42000000'),
                    'min_stock': 3,
                    'max_stock': 30,
                    'description': 'ماشین لباسشویی ال جی 8 کیلویی با موتور اینورتر',
                    'status': 'active',
                    'category': home_cat
                },
                {
                    'product_code': 'TAB001',
                    'name': 'تبلت iPad Air 2022',
                    'barcode': '6260000050001',
                    'base_unit': 'دستگاه',
                    'cost_price': Decimal('28000000'),
                    'sale_price': Decimal('35000000'),
                    'min_stock': 5,
                    'max_stock': 40,
                    'description': 'تبلت اپل آیپد ایر 2022 با صفحه نمایش 10.9 اینچ',
                    'status': 'active',
                    'category': mobile_cat
                },
            ]
            
            for prod_data in products:
                obj, created = Product.objects.get_or_create(
                    product_code=prod_data['product_code'],
                    defaults=prod_data
                )
                if created:
                    self.stdout.write(f'  + {prod_data["name"]}')
            
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.SUCCESS('✅ Database initialized successfully!'))
            self.stdout.write('='*50)
            
            # Show summary
            self.stdout.write('\n📊 Summary:')
            self.stdout.write(f'  • Users: {User.objects.count()}')
            self.stdout.write(f'  • Customers: {Customer.objects.count()}')
            self.stdout.write(f'  • Products: {Product.objects.count()}')
            self.stdout.write(f'  • Customer Categories: {CustomerCategory.objects.count()}')
            self.stdout.write(f'  • Product Categories: {ProductCategory.objects.count()}')
            
            self.stdout.write('\n🔐 Login credentials:')
            self.stdout.write('  URL: http://localhost:8000/admin/')
            self.stdout.write('  Username: admin')
            self.stdout.write('  Password: admin123')
            
            self.stdout.write('\n✨ You can now:')
            self.stdout.write('  1. Login to admin panel')
            self.stdout.write('  2. Access API endpoints')
            self.stdout.write('  3. Start using the system!')