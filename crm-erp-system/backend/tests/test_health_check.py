"""
Tests for health check endpoints
"""
import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestHealthCheck:
    """Test health check endpoints"""
    
    def test_basic_health_check(self, api_client):
        """Test basic health check endpoint"""
        url = reverse('health-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'timestamp' in response.data
        assert response.data['service'] == 'CRM/ERP API'
        assert response.data['version'] == '1.0.0'
    
    def test_detailed_health_check(self, api_client):
        """Test detailed health check endpoint"""
        url = reverse('health-check-detailed')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'status' in response.data
        assert 'components' in response.data
        assert 'database' in response.data['components']
        assert 'system' in response.data
    
    def test_readiness_check(self, api_client, db):
        """Test readiness check endpoint"""
        url = reverse('readiness-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['ready'] == True
        assert 'checks' in response.data
        assert 'database' in response.data['checks']
    
    def test_liveness_check(self, api_client):
        """Test liveness check endpoint"""
        url = reverse('liveness-check')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['alive'] == True
        assert 'timestamp' in response.data
    
    def test_metrics_endpoint(self, api_client, db):
        """Test metrics endpoint"""
        url = reverse('metrics')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'timestamp' in response.data
        assert 'counters' in response.data
        assert 'users' in response.data['counters']
        assert 'customers' in response.data['counters']
        assert 'products' in response.data['counters']