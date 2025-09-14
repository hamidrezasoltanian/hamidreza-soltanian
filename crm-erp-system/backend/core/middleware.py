"""
Custom middleware for the CRM/ERP system
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
import time
import json
import hashlib


class RateLimitMiddleware:
    """
    Custom rate limiting middleware
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Configuration
        self.rate_limit_per_minute = getattr(settings, 'RATE_LIMIT_PER_MINUTE', 60)
        self.rate_limit_per_hour = getattr(settings, 'RATE_LIMIT_PER_HOUR', 1000)
        self.whitelist_paths = [
            '/api/v1/health/',
            '/api/v1/live/',
            '/api/v1/ready/',
            '/api/docs/',
            '/api/redoc/',
            '/admin/',
        ]

    def __call__(self, request):
        # Skip rate limiting for whitelisted paths
        for path in self.whitelist_paths:
            if request.path.startswith(path):
                return self.get_response(request)
        
        # Skip for authenticated superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return self.get_response(request)
        
        # Get client identifier
        client_id = self.get_client_id(request)
        
        # Check rate limits
        if not self.check_rate_limit(client_id):
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': 'Too many requests. Please try again later.',
                'retry_after': 60
            }, status=429)
        
        response = self.get_response(request)
        
        # Add rate limit headers
        self.add_rate_limit_headers(response, client_id)
        
        return response
    
    def get_client_id(self, request):
        """Get unique client identifier"""
        if request.user.is_authenticated:
            return f"user_{request.user.id}"
        
        # Use IP address for anonymous users
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        
        return f"ip_{ip}"
    
    def check_rate_limit(self, client_id):
        """Check if client has exceeded rate limit"""
        now = time.time()
        
        # Check minute limit
        minute_key = f"rate_limit:minute:{client_id}:{int(now // 60)}"
        minute_count = cache.get(minute_key, 0)
        
        if minute_count >= self.rate_limit_per_minute:
            return False
        
        # Check hour limit
        hour_key = f"rate_limit:hour:{client_id}:{int(now // 3600)}"
        hour_count = cache.get(hour_key, 0)
        
        if hour_count >= self.rate_limit_per_hour:
            return False
        
        # Increment counters
        cache.set(minute_key, minute_count + 1, 60)
        cache.set(hour_key, hour_count + 1, 3600)
        
        return True
    
    def add_rate_limit_headers(self, response, client_id):
        """Add rate limit information to response headers"""
        now = time.time()
        
        minute_key = f"rate_limit:minute:{client_id}:{int(now // 60)}"
        minute_count = cache.get(minute_key, 0)
        
        hour_key = f"rate_limit:hour:{client_id}:{int(now // 3600)}"
        hour_count = cache.get(hour_key, 0)
        
        response['X-RateLimit-Limit-Minute'] = str(self.rate_limit_per_minute)
        response['X-RateLimit-Remaining-Minute'] = str(max(0, self.rate_limit_per_minute - minute_count))
        response['X-RateLimit-Limit-Hour'] = str(self.rate_limit_per_hour)
        response['X-RateLimit-Remaining-Hour'] = str(max(0, self.rate_limit_per_hour - hour_count))
        response['X-RateLimit-Reset'] = str(int((now // 60 + 1) * 60))


class RequestLoggingMiddleware:
    """
    Middleware to log API requests
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.skip_paths = [
            '/api/v1/health/',
            '/api/v1/live/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Skip logging for certain paths
        for path in self.skip_paths:
            if request.path.startswith(path):
                return self.get_response(request)
        
        start_time = time.time()
        
        # Log request
        request_data = {
            'timestamp': timezone.now().isoformat(),
            'method': request.method,
            'path': request.path,
            'user': str(request.user) if request.user.is_authenticated else 'anonymous',
            'ip': self.get_client_ip(request),
        }
        
        response = self.get_response(request)
        
        # Log response
        duration = time.time() - start_time
        request_data.update({
            'status_code': response.status_code,
            'duration_ms': round(duration * 1000, 2)
        })
        
        # Store in cache for metrics
        self.store_metrics(request_data)
        
        # Log to file if configured
        if getattr(settings, 'LOG_API_REQUESTS', False):
            self.log_to_file(request_data)
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def store_metrics(self, data):
        """Store metrics in cache for monitoring"""
        try:
            # Store recent requests
            key = 'api_metrics:recent_requests'
            recent = cache.get(key, [])
            recent.append(data)
            # Keep only last 100 requests
            if len(recent) > 100:
                recent = recent[-100:]
            cache.set(key, recent, 3600)
            
            # Update counters
            status_key = f"api_metrics:status:{data['status_code']}"
            cache.set(status_key, cache.get(status_key, 0) + 1, 3600)
            
            method_key = f"api_metrics:method:{data['method']}"
            cache.set(method_key, cache.get(method_key, 0) + 1, 3600)
        except:
            pass
    
    def log_to_file(self, data):
        """Log request data to file"""
        try:
            import logging
            logger = logging.getLogger('api_requests')
            logger.info(json.dumps(data))
        except:
            pass


class SecurityHeadersMiddleware:
    """
    Add security headers to responses
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # CSP header for API responses
        if request.path.startswith('/api/'):
            response['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none';"
        
        return response