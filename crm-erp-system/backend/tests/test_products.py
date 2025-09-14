"""
Tests for Product API endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status
from products.models import Product
from tests.factories import ProductFactory, ProductCategoryFactory
from decimal import Decimal


@pytest.mark.django_db
class TestProductAPI:
    """Test Product API endpoints"""
    
    def test_list_products_unauthorized(self, api_client):
        """Test that unauthorized users cannot list products"""
        url = reverse('product-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_products_authorized(self, authenticated_client):
        """Test listing products with authentication"""
        ProductFactory.create_batch(5)
        
        url = reverse('product-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert len(response.data['results']) == 5
    
    def test_create_product(self, authenticated_client):
        """Test creating a new product"""
        category = ProductCategoryFactory()
        
        url = reverse('product-list')
        data = {
            'product_code': 'P9999',
            'name': 'محصول تست',
            'barcode': '1234567890123',
            'category': category.id,
            'base_unit': 'عدد',
            'cost_price': '1000000',
            'sale_price': '1500000',
            'min_stock': 5,
            'max_stock': 100,
            'description': 'توضیحات محصول تست',
            'status': 'active'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.filter(product_code='P9999').exists()
    
    def test_retrieve_product(self, authenticated_client):
        """Test retrieving a single product"""
        product = ProductFactory()
        
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['product_code'] == product.product_code
    
    def test_update_product_price(self, authenticated_client):
        """Test updating product price"""
        product = ProductFactory(sale_price=Decimal('1000000'))
        
        url = reverse('product-detail', kwargs={'pk': product.pk})
        data = {
            'sale_price': '1200000'
        }
        
        response = authenticated_client.patch(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        product.refresh_from_db()
        assert product.sale_price == Decimal('1200000')
    
    def test_delete_product(self, admin_client):
        """Test deleting a product (admin only)"""
        product = ProductFactory()
        
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = admin_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(pk=product.pk).exists()
    
    def test_search_products(self, authenticated_client):
        """Test searching products by name"""
        ProductFactory(name='لپ تاپ ASUS')
        ProductFactory(name='موبایل Samsung')
        ProductFactory(name='تبلت iPad')
        
        url = reverse('product-list')
        response = authenticated_client.get(url, {'search': 'موبایل'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert 'Samsung' in response.data['results'][0]['name']
    
    def test_filter_products_by_category(self, authenticated_client):
        """Test filtering products by category"""
        cat1 = ProductCategoryFactory(name='الکترونیک')
        cat2 = ProductCategoryFactory(name='لوازم خانگی')
        
        ProductFactory.create_batch(3, category=cat1)
        ProductFactory.create_batch(2, category=cat2)
        
        url = reverse('product-list')
        response = authenticated_client.get(url, {'category': cat1.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3
    
    def test_filter_products_by_price_range(self, authenticated_client):
        """Test filtering products by price range"""
        ProductFactory(sale_price=Decimal('500000'))
        ProductFactory(sale_price=Decimal('1000000'))
        ProductFactory(sale_price=Decimal('1500000'))
        ProductFactory(sale_price=Decimal('2000000'))
        
        url = reverse('product-list')
        response = authenticated_client.get(url, {
            'min_price': '1000000',
            'max_price': '1500000'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
    
    def test_product_stock_validation(self, authenticated_client):
        """Test product stock validation"""
        url = reverse('product-list')
        data = {
            'product_code': 'P8888',
            'name': 'محصول با موجودی نامعتبر',
            'barcode': '9876543210123',
            'base_unit': 'عدد',
            'cost_price': '1000000',
            'sale_price': '1500000',
            'min_stock': 100,  # Min greater than max
            'max_stock': 50,
            'status': 'active'
        }
        
        response = authenticated_client.post(url, data, format='json')
        
        # Should fail validation
        assert response.status_code == status.HTTP_400_BAD_REQUEST