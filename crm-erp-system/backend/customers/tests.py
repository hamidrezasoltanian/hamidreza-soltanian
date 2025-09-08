import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date
from .models import Customer, CustomerPersonnel
from .factories import CustomerFactory, CustomerPersonnelFactory


@pytest.mark.unit
class CustomerModelTest(TestCase):
    def setUp(self):
        self.customer = CustomerFactory()

    def test_customer_creation(self):
        """Test customer creation with required fields"""
        customer = Customer.objects.create(
            customer_code="CUST001",
            first_name="علی",
            last_name="احمدی",
            company_name="شرکت تست",
            national_id="1234567890",
            economic_code="1234567890123456",
            postal_code="1234567890",
            phone="02112345678",
            email="test@example.com",
            address="تهران، خیابان تست",
            city="تهران",
            province="تهران",
            country="ایران"
        )
        self.assertEqual(customer.customer_code, "CUST001")
        self.assertEqual(customer.first_name, "علی")
        self.assertEqual(customer.last_name, "احمدی")
        self.assertTrue(customer.is_active)

    def test_customer_str_representation(self):
        """Test string representation of customer"""
        expected = f"{self.customer.first_name} {self.customer.last_name} - {self.customer.company_name}"
        self.assertEqual(str(self.customer), expected)

    def test_customer_validation(self):
        """Test customer field validation"""
        with self.assertRaises(ValidationError):
            customer = Customer(
                customer_code="",  # Empty customer code should fail
                first_name="علی",
                last_name="احمدی"
            )
            customer.full_clean()

    def test_customer_unique_code(self):
        """Test customer code uniqueness"""
        CustomerFactory(customer_code="UNIQUE001")
        with self.assertRaises(Exception):  # Should raise IntegrityError
            CustomerFactory(customer_code="UNIQUE001")

    def test_customer_phone_validation(self):
        """Test phone number validation"""
        customer = CustomerFactory()
        # Test valid phone numbers
        valid_phones = ["02112345678", "09123456789", "+982112345678"]
        for phone in valid_phones:
            customer.phone = phone
            customer.full_clean()  # Should not raise exception

    def test_customer_email_validation(self):
        """Test email validation"""
        customer = CustomerFactory()
        # Test valid email
        customer.email = "test@example.com"
        customer.full_clean()  # Should not raise exception

        # Test invalid email
        with self.assertRaises(ValidationError):
            customer.email = "invalid-email"
            customer.full_clean()


@pytest.mark.unit
class CustomerPersonnelModelTest(TestCase):
    def setUp(self):
        self.customer = CustomerFactory()
        self.personnel = CustomerPersonnelFactory(customer=self.customer)

    def test_personnel_creation(self):
        """Test personnel creation"""
        personnel = CustomerPersonnel.objects.create(
            customer=self.customer,
            first_name="محمد",
            last_name="رضایی",
            position="مدیر فروش",
            phone="09123456789",
            email="mohammad@example.com",
            is_primary=True
        )
        self.assertEqual(personnel.customer, self.customer)
        self.assertEqual(personnel.first_name, "محمد")
        self.assertTrue(personnel.is_primary)

    def test_personnel_str_representation(self):
        """Test string representation of personnel"""
        expected = f"{self.personnel.first_name} {self.personnel.last_name} - {self.personnel.position}"
        self.assertEqual(str(self.personnel), expected)

    def test_personnel_phone_validation(self):
        """Test personnel phone validation"""
        personnel = CustomerPersonnelFactory(customer=self.customer)
        # Test valid phone numbers
        valid_phones = ["02112345678", "09123456789", "+982112345678"]
        for phone in valid_phones:
            personnel.phone = phone
            personnel.full_clean()  # Should not raise exception

    def test_personnel_email_validation(self):
        """Test personnel email validation"""
        personnel = CustomerPersonnelFactory(customer=self.customer)
        # Test valid email
        personnel.email = "test@example.com"
        personnel.full_clean()  # Should not raise exception

        # Test invalid email
        with self.assertRaises(ValidationError):
            personnel.email = "invalid-email"
            personnel.full_clean()

    def test_personnel_primary_constraint(self):
        """Test that only one personnel can be primary per customer"""
        # Create first primary personnel
        CustomerPersonnelFactory(customer=self.customer, is_primary=True)
        
        # Try to create another primary personnel
        with self.assertRaises(Exception):  # Should raise IntegrityError
            CustomerPersonnelFactory(customer=self.customer, is_primary=True)


@pytest.mark.unit
class CustomerModelMethodsTest(TestCase):
    def setUp(self):
        self.customer = CustomerFactory()

    def test_get_full_name(self):
        """Test get_full_name method"""
        expected = f"{self.customer.first_name} {self.customer.last_name}"
        self.assertEqual(self.customer.get_full_name(), expected)

    def test_get_primary_personnel(self):
        """Test get_primary_personnel method"""
        # Create primary personnel
        primary = CustomerPersonnelFactory(customer=self.customer, is_primary=True)
        # Create non-primary personnel
        CustomerPersonnelFactory(customer=self.customer, is_primary=False)
        
        self.assertEqual(self.customer.get_primary_personnel(), primary)

    def test_get_all_personnel(self):
        """Test get_all_personnel method"""
        # Create multiple personnel
        CustomerPersonnelFactory(customer=self.customer, is_primary=True)
        CustomerPersonnelFactory(customer=self.customer, is_primary=False)
        
        personnel_count = self.customer.get_all_personnel().count()
        self.assertEqual(personnel_count, 2)

    def test_is_company(self):
        """Test is_company method"""
        # Test with company name
        self.customer.company_name = "شرکت تست"
        self.assertTrue(self.customer.is_company())
        
        # Test without company name
        self.customer.company_name = ""
        self.assertFalse(self.customer.is_company())

    def test_get_display_name(self):
        """Test get_display_name method"""
        # Test with company name
        self.customer.company_name = "شرکت تست"
        self.assertEqual(self.customer.get_display_name(), "شرکت تست")
        
        # Test without company name
        self.customer.company_name = ""
        expected = f"{self.customer.first_name} {self.customer.last_name}"
        self.assertEqual(self.customer.get_display_name(), expected)