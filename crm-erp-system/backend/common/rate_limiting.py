from django.core.cache import cache
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from functools import wraps
import time
import hashlib


class RateLimiter:
    def __init__(self, requests=100, window=3600, key_func=None):
        self.requests = requests
        self.window = window
        self.key_func = key_func or self.default_key_func
    
    def default_key_func(self, request):
        """Default key function based on IP and user"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"rate_limit_user_{request.user.id}"
        return f"rate_limit_ip_{self.get_client_ip(request)}"
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_allowed(self, request):
        """Check if request is allowed"""
        key = self.key_func(request)
        current_time = int(time.time())
        window_start = current_time - self.window
        
        # Get current requests in window
        requests = cache.get(key, [])
        
        # Remove old requests outside window
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Check if under limit
        if len(requests) >= self.requests:
            return False, len(requests)
        
        # Add current request
        requests.append(current_time)
        cache.set(key, requests, self.window)
        
        return True, len(requests)
    
    def get_remaining_requests(self, request):
        """Get remaining requests in current window"""
        key = self.key_func(request)
        current_time = int(time.time())
        window_start = current_time - self.window
        
        requests = cache.get(key, [])
        requests = [req_time for req_time in requests if req_time > window_start]
        
        return max(0, self.requests - len(requests))


def rate_limit(requests=100, window=3600, key_func=None):
    """Rate limiting decorator"""
    limiter = RateLimiter(requests, window, key_func)
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            allowed, current_count = limiter.is_allowed(request)
            
            if not allowed:
                remaining = limiter.get_remaining_requests(request)
                reset_time = int(time.time()) + limiter.window
                
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'limit': limiter.requests,
                    'current': current_count,
                    'remaining': remaining,
                    'reset_time': reset_time
                }, status=429)
                
                response['X-RateLimit-Limit'] = limiter.requests
                response['X-RateLimit-Remaining'] = remaining
                response['X-RateLimit-Reset'] = reset_time
                
                return response
            
            # Add rate limit headers to successful response
            response = view_func(request, *args, **kwargs)
            remaining = limiter.get_remaining_requests(request)
            reset_time = int(time.time()) + limiter.window
            
            response['X-RateLimit-Limit'] = limiter.requests
            response['X-RateLimit-Remaining'] = remaining
            response['X-RateLimit-Reset'] = reset_time
            
            return response
        
        return wrapper
    return decorator


def rate_limit_class(requests=100, window=3600, key_func=None):
    """Rate limiting decorator for class-based views"""
    def decorator(cls):
        original_dispatch = cls.dispatch
        
        def dispatch(self, request, *args, **kwargs):
            limiter = RateLimiter(requests, window, key_func)
            allowed, current_count = limiter.is_allowed(request)
            
            if not allowed:
                remaining = limiter.get_remaining_requests(request)
                reset_time = int(time.time()) + limiter.window
                
                response = JsonResponse({
                    'error': 'Rate limit exceeded',
                    'limit': limiter.requests,
                    'current': current_count,
                    'remaining': remaining,
                    'reset_time': reset_time
                }, status=429)
                
                response['X-RateLimit-Limit'] = limiter.requests
                response['X-RateLimit-Remaining'] = remaining
                response['X-RateLimit-Reset'] = reset_time
                
                return response
            
            # Call original dispatch
            response = original_dispatch(self, request, *args, **kwargs)
            
            # Add rate limit headers
            remaining = limiter.get_remaining_requests(request)
            reset_time = int(time.time()) + limiter.window
            
            response['X-RateLimit-Limit'] = limiter.requests
            response['X-RateLimit-Remaining'] = remaining
            response['X-RateLimit-Reset'] = reset_time
            
            return response
        
        cls.dispatch = dispatch
        return cls
    
    return decorator


# Predefined rate limiters
class RateLimiters:
    # API endpoints
    API_GENERAL = rate_limit(requests=1000, window=3600)  # 1000 requests per hour
    API_AUTH = rate_limit(requests=10, window=3600)  # 10 login attempts per hour
    API_CREATE = rate_limit(requests=100, window=3600)  # 100 creates per hour
    API_UPDATE = rate_limit(requests=500, window=3600)  # 500 updates per hour
    
    # Admin endpoints
    ADMIN_GENERAL = rate_limit(requests=200, window=3600)  # 200 requests per hour
    ADMIN_BULK = rate_limit(requests=10, window=3600)  # 10 bulk operations per hour
    
    # Public endpoints
    PUBLIC_READ = rate_limit(requests=10000, window=3600)  # 10000 reads per hour