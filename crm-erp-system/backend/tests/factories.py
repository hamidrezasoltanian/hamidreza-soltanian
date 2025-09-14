"""
Factory classes for generating test data
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from decimal import Decimal
from django.contrib.auth.models import User
from customers.models import Customer, CustomerCategory
from products.models import Product, ProductCategory
from invoices.models import Invoice, InvoiceItem


fake = Faker('fa_IR')  # Persian locale


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class CustomerCategoryFactory(DjangoModelFactory):
    class Meta:
        model = CustomerCategory
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    color = factory.Faker('hex_color')
    is_active = True


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer
    
    customer_code = factory.Sequence(lambda n: f'C{n:04d}')
    customer_type = factory.Faker('random_element', elements=['individual', 'legal'])
    first_name = factory.Faker('first_name', locale='fa_IR')
    last_name = factory.Faker('last_name', locale='fa_IR')
    company_name = factory.Faker('company', locale='fa_IR')
    national_id = factory.Faker('numerify', text='##########')
    economic_code = factory.Faker('numerify', text='############')
    phone_number = factory.Faker('numerify', text='021########')
    mobile_number = factory.Faker('numerify', text='0912#######')
    email = factory.Faker('email')
    address = factory.Faker('address', locale='fa_IR')
    city = factory.Faker('city', locale='fa_IR')
    state = factory.Faker('state', locale='fa_IR')
    postal_code = factory.Faker('postcode')
    credit_limit = factory.Faker('pydecimal', left_digits=9, right_digits=0, positive=True)
    status = 'active'


class ProductCategoryFactory(DjangoModelFactory):
    class Meta:
        model = ProductCategory
    
    name = factory.Faker('word')
    description = factory.Faker('text', max_nb_chars=200)
    is_active = True


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = Product
    
    product_code = factory.Sequence(lambda n: f'P{n:04d}')
    name = factory.Faker('word')
    barcode = factory.Faker('ean13')
    category = factory.SubFactory(ProductCategoryFactory)
    base_unit = factory.Faker('random_element', elements=['عدد', 'کیلو', 'متر', 'بسته'])
    cost_price = factory.Faker('pydecimal', left_digits=8, right_digits=0, positive=True)
    sale_price = factory.LazyAttribute(lambda obj: obj.cost_price * Decimal('1.3'))
    wholesale_price = factory.LazyAttribute(lambda obj: obj.cost_price * Decimal('1.2'))
    min_stock = factory.Faker('random_int', min=1, max=10)
    max_stock = factory.Faker('random_int', min=50, max=200)
    description = factory.Faker('text', max_nb_chars=500)
    status = 'active'


class InvoiceFactory(DjangoModelFactory):
    class Meta:
        model = Invoice
    
    invoice_number = factory.Sequence(lambda n: f'INV-{n:05d}')
    customer = factory.SubFactory(CustomerFactory)
    invoice_date = factory.Faker('date_this_year')
    due_date = factory.Faker('future_date', end_date='+30d')
    status = factory.Faker('random_element', elements=['draft', 'approved', 'paid'])
    payment_method = factory.Faker('random_element', elements=['cash', 'credit', 'check'])
    discount_percentage = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, max_value=20)


class InvoiceItemFactory(DjangoModelFactory):
    class Meta:
        model = InvoiceItem
    
    invoice = factory.SubFactory(InvoiceFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Faker('random_int', min=1, max=10)
    unit_price = factory.LazyAttribute(lambda obj: obj.product.sale_price)
    discount_percentage = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True, max_value=10)
    tax_rate = Decimal('9')  # 9% VAT