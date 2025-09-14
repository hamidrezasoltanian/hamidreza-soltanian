"""
Tests for Customer API endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from customers.models import Customer
from tests.factories import CustomerFactory, CustomerCategoryFactory


@pytest.mark.django_db
class TestCustomerAPI:
    """Test Customer API endpoints"""
    
    def test_list_customers_unauthorized(self, api_client):
        """Test that unauthorized users cannot list customers"""
        url = reverse('customer-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_customers_authorized(self, authenticated_client):
        """Test listing customers with authentication"""
        # Create test customers
        CustomerFactory.create_batch(3)
        
        url = reverse('customer-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 3
    
    def test_create_customer(self, authenticated_client):
        """Test creating a new customer"""
        category = CustomerCategoryFactory()
        
        url = reverse('customer-list')
        data = {
            'customer_code': 'C9999',
            'customer_type': 'individual',
            'first_name': 'علی',
            'last_name': 'احمدی',
            'national_id': '1234567890',
            'mobile_number': '09121234567',
            'email': 'ali@example.com',
            'address': 'تهران، خیابان ولیعصر',
            'city': 'تهران',
            'state': 'تهران',
            'credit_limit': '50000000',
            'status': 'active'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Customer.objects.filter(customer_code='C9999').exists()
    
    def test_retrieve_customer(self, authenticated_client):
        """Test retrieving a single customer"""
        customer = CustomerFactory()
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['customer_code'] == customer.customer_code
    
    def test_update_customer(self, authenticated_client):
        """Test updating a customer"""
        customer = CustomerFactory()
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        data = {
            'credit_limit': '100000000'
        }
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        customer.refresh_from_db()
        assert str(customer.credit_limit) == '100000000'
    
    def test_delete_customer(self, admin_client):
        """Test deleting a customer (admin only)"""
        customer = CustomerFactory()
        
        url = reverse('customer-detail', kwargs={'pk': customer.pk})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Customer.objects.filter(pk=customer.pk).exists()
    
    def test_search_customers(self, authenticated_client):
        """Test searching customers"""
        CustomerFactory(first_name='علی', last_name='رضایی')
        CustomerFactory(first_name='محمد', last_name='احمدی')
        CustomerFactory(first_name='زهرا', last_name='محمدی')
        
        url = reverse('customer-list')
        response = authenticated_client.get(url, {'search': 'محمد'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_filter_customers_by_type(self, authenticated_client):
        """Test filtering customers by type"""
        CustomerFactory.create_batch(2, customer_type='individual')
        CustomerFactory.create_batch(3, customer_type='legal')
        
        url = reverse('customer-list')
        response = authenticated_client.get(url, {'customer_type': 'legal'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_pagination(self, authenticated_client):
        """Test pagination of customer list"""
        CustomerFactory.create_batch(25)
        
        url = reverse('customer-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert len(response.data['results']) == 20  # Default page size