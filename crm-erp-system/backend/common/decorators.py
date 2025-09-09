from functools import wraps
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
import hashlib
import json


def cache_view(timeout=300, key_prefix=''):
    """
    Cache decorator for class-based views
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(self, request, *args, **kwargs):
            # Create cache key based on request parameters
            cache_key = f"{key_prefix}_{request.user.id}_{request.get_full_path()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute view and cache result
            result = view_func(self, request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def cache_method(timeout=300, key_prefix=''):
    """
    Cache decorator for methods
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key_data = f"{key_prefix}_{func.__name__}_{str(args)}_{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute method and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate cache entries matching a pattern
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            # Invalidate cache (simplified - in production use Redis SCAN)
            cache.delete_many(cache.keys(f"*{pattern}*"))
            return result
        return wrapper
    return decorator


class CacheMixin:
    """
    Mixin for adding cache functionality to viewsets
    """
    cache_timeout = 300
    cache_key_prefix = ''
    
    def get_cache_key(self, request, *args, **kwargs):
        """Generate cache key for the request"""
        key_data = f"{self.cache_key_prefix}_{request.user.id}_{request.get_full_path()}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get_cached_data(self, request, *args, **kwargs):
        """Get data from cache"""
        cache_key = self.get_cache_key(request, *args, **kwargs)
        return cache.get(cache_key)
    
    def set_cached_data(self, data, request, *args, **kwargs):
        """Set data in cache"""
        cache_key = self.get_cache_key(request, *args, **kwargs)
        cache.set(cache_key, data, self.cache_timeout)
        return data