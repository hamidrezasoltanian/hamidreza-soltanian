"""
Simple seed data for testing
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal
import random

from customers.models import Customer, CustomerCategory
from products.models import Product, ProductCategory
from personnel.models import Personnel, Department, Position


class Command(BaseCommand):
    help = 'Seeds the database with simple test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('🌱 Starting to seed database with simple data...')
        
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
                self.stdout.write('✓ Superuser created (username: admin, password: admin123)')
            
            # Create departments
            dept_data = [
                {'name': 'مدیریت', 'code': 'MGT'},
                {'name': 'فروش', 'code': 'SLS'},
                {'name': 'حسابداری', 'code': 'ACC'},
            ]
            for dept in dept_data:
                Department.objects.get_or_create(**dept)
            self.stdout.write('✓ Departments created')
            
            # Create positions
            pos_data = [
                {'title': 'مدیرعامل', 'level': 1},
                {'title': 'مدیر فروش', 'level': 2},
                {'title': 'کارشناس فروش', 'level': 3},
            ]
            for pos in pos_data:
                Position.objects.get_or_create(**pos)
            self.stdout.write('✓ Positions created')
            
            # Create customer categories
            cat_data = [
                {'name': 'عمده فروش', 'code': 'WHOLESALE'},
                {'name': 'خرده فروش', 'code': 'RETAIL'},
                {'name': 'VIP', 'code': 'VIP'},
            ]
            for cat in cat_data:
                CustomerCategory.objects.get_or_create(**cat)
            self.stdout.write('✓ Customer categories created')
            
            # Create product categories
            prod_cat_data = [
                {'name': 'الکترونیک', 'code': 'ELEC'},
                {'name': 'لوازم خانگی', 'code': 'HOME'},
            ]
            for cat in prod_cat_data:
                ProductCategory.objects.get_or_create(**cat)
            self.stdout.write('✓ Product categories created')
            
            # Create personnel
            dept = Department.objects.get(code='SLS')
            pos = Position.objects.get(title='کارشناس فروش')
            
            Personnel.objects.get_or_create(
                personnel_code='P001',
                defaults={
                    'first_name': 'علی',
                    'last_name': 'احمدی',
                    'national_code': '0012345678',
                    'department': dept,
                    'position': pos,
                    'mobile': '09121234567',
                    'is_active': True
                }
            )
            self.stdout.write('✓ Personnel created')
            
            # Create customers
            customers_data = [
                {
                    'customer_code': 'C001',
                    'customer_type': 'legal',
                    'company_name': 'شرکت نوآوران',
                    'first_name': 'شرکت',
                    'last_name': 'نوآوران',
                    'national_id': '14007654321',
                    'economic_code': '411234567890',
                    'phone': '02188776655',
                    'mobile': '09121234567',
                    'email': 'info@navaran.com',
                    'address': 'تهران، خیابان ولیعصر',
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
                    'email': 'mohammad@gmail.com',
                    'address': 'تهران، سعادت آباد',
                    'credit_limit': Decimal('50000000'),
                    'is_active': True
                },
            ]
            
            categories = list(CustomerCategory.objects.all())
            for data in customers_data:
                customer, created = Customer.objects.get_or_create(
                    customer_code=data['customer_code'],
                    defaults=data
                )
                if created and categories:
                    customer.category = random.choice(categories)
                    customer.save()
            self.stdout.write('✓ Customers created')
            
            # Create products
            products_data = [
                {
                    'name': 'لپ تاپ ASUS',
                    'code': 'LAP001',
                    'barcode': '6260000010001',
                    'unit': 'دستگاه',
                    'purchase_price': Decimal('25000000'),
                    'sale_price': Decimal('32000000'),
                    'min_stock': 5,
                    'max_stock': 50,
                    'is_active': True
                },
                {
                    'name': 'موبایل Samsung',
                    'code': 'MOB001',
                    'barcode': '6260000020001',
                    'unit': 'دستگاه',
                    'purchase_price': Decimal('15000000'),
                    'sale_price': Decimal('18000000'),
                    'min_stock': 10,
                    'max_stock': 100,
                    'is_active': True
                },
                {
                    'name': 'یخچال سامسونگ',
                    'code': 'REF001',
                    'barcode': '6260000030001',
                    'unit': 'دستگاه',
                    'purchase_price': Decimal('45000000'),
                    'sale_price': Decimal('55000000'),
                    'min_stock': 2,
                    'max_stock': 20,
                    'is_active': True
                },
            ]
            
            prod_categories = list(ProductCategory.objects.all())
            for data in products_data:
                product, created = Product.objects.get_or_create(
                    code=data['code'],
                    defaults=data
                )
                if created and prod_categories:
                    product.category = random.choice(prod_categories)
                    product.save()
            self.stdout.write('✓ Products created')
            
        self.stdout.write(self.style.SUCCESS('✅ Database seeded successfully!'))