import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from .logging_config import PerformanceLogger, SecurityLogger
from .rate_limiting import RateLimiter


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor API performance"""
    
    def process_request(self, request):
        request._start_time = time.time()
        request._query_count_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            query_count = len(connection.queries) - getattr(request, '_query_count_start', 0)
            
            # Log API performance
            PerformanceLogger.log_api_request(request, response, duration, query_count)
            
            # Add performance headers
            response['X-Response-Time'] = f"{duration:.3f}s"
            response['X-Query-Count'] = str(query_count)
            
            # Log slow requests
            if duration > 1.0:  # More than 1 second
                PerformanceLogger.log_slow_query(
                    f"{request.method} {request.path}",
                    duration,
                    {"query_count": query_count}
                )
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers"""
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        
        # HSTS (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """Middleware for rate limiting"""
    
    def process_request(self, request):
        # Skip rate limiting for certain paths
        skip_paths = ['/admin/', '/static/', '/media/', '/favicon.ico']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Different rate limits for different endpoints
        if request.path.startswith('/api/v1/auth/'):
            limiter = RateLimiter(requests=10, window=3600)  # 10 auth requests per hour
        elif request.path.startswith('/api/v1/'):
            limiter = RateLimiter(requests=1000, window=3600)  # 1000 API requests per hour
        else:
            return None
        
        allowed, current_count = limiter.is_allowed(request)
        
        if not allowed:
            from django.http import JsonResponse
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
        
        return None


class QueryCountMiddleware(MiddlewareMixin):
    """Middleware to monitor database query count"""
    
    def process_request(self, request):
        request._query_count_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_query_count_start'):
            query_count = len(connection.queries) - request._query_count_start
            response['X-Query-Count'] = str(query_count)
            
            # Log excessive queries
            if query_count > 20:  # More than 20 queries
                PerformanceLogger.log_slow_query(
                    f"Excessive queries: {request.method} {request.path}",
                    0,
                    {"query_count": query_count}
                )
        
        return response


class SecurityEventMiddleware(MiddlewareMixin):
    """Middleware to log security events"""
    
    def process_request(self, request):
        # Log suspicious patterns
        suspicious_patterns = [
            '..',  # Path traversal
            'script',  # XSS attempts
            'union',  # SQL injection
            'select',  # SQL injection
            'drop',  # SQL injection
        ]
        
        for pattern in suspicious_patterns:
            if pattern in request.path.lower() or pattern in str(request.GET).lower():
                SecurityLogger.log_suspicious_activity(
                    request.user if hasattr(request, 'user') else None,
                    'suspicious_pattern',
                    request.META.get('REMOTE_ADDR'),
                    {'pattern': pattern, 'path': request.path}
                )
                break
        
        return None