from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
import os
import sys
import platform


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Basic health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'CRM/ERP API',
        'version': '1.0.0'
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """Detailed health check with component status"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'CRM/ERP API',
        'version': '1.0.0',
        'components': {}
    }
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['components']['database'] = {
            'status': 'healthy',
            'type': 'sqlite3',
            'response_time_ms': 1
        }
    except Exception as e:
        health_status['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        health_status['status'] = 'unhealthy'
    
    # Check cache (Redis)
    try:
        cache.set('health_check', 'ok', 1)
        if cache.get('health_check') == 'ok':
            health_status['components']['cache'] = {
                'status': 'healthy',
                'type': 'redis'
            }
        else:
            raise Exception("Cache not working")
    except:
        health_status['components']['cache'] = {
            'status': 'degraded',
            'type': 'fallback',
            'message': 'Using default cache backend'
        }
    
    # System info
    health_status['system'] = {
        'python_version': sys.version.split()[0],
        'platform': platform.platform(),
        'processor': platform.processor() or 'unknown',
        'architecture': platform.machine()
    }
    
    # Disk space
    try:
        stat = os.statvfs('/')
        total = stat.f_blocks * stat.f_frsize
        free = stat.f_available * stat.f_frsize
        used_percent = ((total - free) / total) * 100
        
        health_status['components']['disk'] = {
            'status': 'healthy' if used_percent < 90 else 'warning',
            'used_percent': round(used_percent, 2),
            'free_gb': round(free / (1024**3), 2)
        }
    except:
        health_status['components']['disk'] = {
            'status': 'unknown'
        }
    
    # Memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_status['components']['memory'] = {
            'status': 'healthy' if memory.percent < 90 else 'warning',
            'used_percent': memory.percent,
            'available_gb': round(memory.available / (1024**3), 2)
        }
    except ImportError:
        health_status['components']['memory'] = {
            'status': 'unknown',
            'message': 'psutil not installed'
        }
    
    # Overall status
    if any(comp.get('status') == 'unhealthy' for comp in health_status['components'].values()):
        health_status['status'] = 'unhealthy'
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif any(comp.get('status') in ['warning', 'degraded'] for comp in health_status['components'].values()):
        health_status['status'] = 'degraded'
        status_code = status.HTTP_200_OK
    else:
        status_code = status.HTTP_200_OK
    
    return Response(health_status, status=status_code)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """Check if the service is ready to accept requests"""
    ready = True
    checks = {}
    
    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM auth_user")
            count = cursor.fetchone()[0]
            checks['database'] = {'ready': True, 'users': count}
    except Exception as e:
        checks['database'] = {'ready': False, 'error': str(e)}
        ready = False
    
    # Check required tables
    try:
        from customers.models import Customer
        from products.models import Product
        checks['models'] = {
            'ready': True,
            'customers': Customer.objects.count(),
            'products': Product.objects.count()
        }
    except Exception as e:
        checks['models'] = {'ready': False, 'error': str(e)}
        ready = False
    
    response_data = {
        'ready': ready,
        'timestamp': timezone.now().isoformat(),
        'checks': checks
    }
    
    return Response(
        response_data,
        status=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """Simple liveness probe for container orchestration"""
    return Response({
        'alive': True,
        'timestamp': timezone.now().isoformat()
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def metrics(request):
    """Basic metrics endpoint"""
    from django.contrib.auth.models import User
    from customers.models import Customer
    from products.models import Product
    from invoices.models import Invoice
    
    metrics_data = {
        'timestamp': timezone.now().isoformat(),
        'counters': {
            'users': User.objects.count(),
            'customers': Customer.objects.count(),
            'products': Product.objects.count(),
            'invoices': Invoice.objects.count(),
        },
        'database': {
            'queries_count': len(connection.queries) if settings.DEBUG else 'N/A',
        }
    }
    
    # Add more metrics as needed
    try:
        from django.core.cache import cache
        cache_key = 'metrics_requests_count'
        requests_count = cache.get(cache_key, 0)
        cache.set(cache_key, requests_count + 1, 3600)
        metrics_data['requests'] = {
            'count_last_hour': requests_count
        }
    except:
        pass
    
    return Response(metrics_data)


# Import settings for metrics
from django.conf import settings