import factory
from factory.django import DjangoModelFactory
from faker import Faker
from .models import Customer, CustomerPersonnel

fake = Faker('fa_IR')


class CustomerFactory(DjangoModelFactory):
    class Meta:
        model = Customer

    customer_code = factory.Sequence(lambda n: f"CUST{n:04d}")
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    company_name = factory.LazyFunction(lambda: fake.company())
    national_id = factory.LazyFunction(lambda: fake.numerify('##########'))
    economic_code = factory.LazyFunction(lambda: fake.numerify('###############'))
    postal_code = factory.LazyFunction(lambda: fake.numerify('##########'))
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.LazyFunction(lambda: fake.email())
    address = factory.LazyFunction(lambda: fake.address())
    city = factory.LazyFunction(lambda: fake.city())
    province = factory.LazyFunction(lambda: fake.state())
    country = "ایران"
    is_active = True
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))


class CustomerPersonnelFactory(DjangoModelFactory):
    class Meta:
        model = CustomerPersonnel

    customer = factory.SubFactory(CustomerFactory)
    first_name = factory.LazyFunction(lambda: fake.first_name())
    last_name = factory.LazyFunction(lambda: fake.last_name())
    position = factory.LazyFunction(lambda: fake.job())
    phone = factory.LazyFunction(lambda: fake.phone_number())
    email = factory.LazyFunction(lambda: fake.email())
    is_primary = False
    notes = factory.LazyFunction(lambda: fake.text(max_nb_chars=100))