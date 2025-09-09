import logging
import logging.config
import structlog
from django.conf import settings
import os


def configure_logging():
    """Configure structured logging for the application"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Django logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                '()': 'structlog.stdlib.ProcessorFormatter',
                'processor': structlog.dev.ConsoleRenderer(colors=False),
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'json',
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_dir, 'django.log'),
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'json',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_dir, 'error.log'),
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'security_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_dir, 'security.log'),
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'json',
            },
            'performance_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(logs_dir, 'performance.log'),
                'maxBytes': 1024*1024*15,  # 15MB
                'backupCount': 10,
                'formatter': 'json',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True,
            },
            'django.request': {
                'handlers': ['error_file'],
                'level': 'ERROR',
                'propagate': True,
            },
            'security': {
                'handlers': ['security_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            'performance': {
                'handlers': ['performance_file'],
                'level': 'INFO',
                'propagate': False,
            },
            'crm_erp': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    return LOGGING


# Logger instances
security_logger = structlog.get_logger('security')
performance_logger = structlog.get_logger('performance')
app_logger = structlog.get_logger('crm_erp')


class SecurityLogger:
    """Security event logger"""
    
    @staticmethod
    def log_login_attempt(user, ip_address, success, failure_reason=None, user_agent=None):
        security_logger.info(
            "login_attempt",
            user_id=user.id if user else None,
            username=user.username if user else None,
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_2fa_event(user, event_type, ip_address, details=None):
        security_logger.info(
            "2fa_event",
            user_id=user.id,
            username=user.username,
            event_type=event_type,
            ip_address=ip_address,
            details=details or {}
        )
    
    @staticmethod
    def log_suspicious_activity(user, activity_type, ip_address, details=None):
        security_logger.warning(
            "suspicious_activity",
            user_id=user.id if user else None,
            username=user.username if user else None,
            activity_type=activity_type,
            ip_address=ip_address,
            details=details or {}
        )


class PerformanceLogger:
    """Performance monitoring logger"""
    
    @staticmethod
    def log_api_request(request, response, duration, query_count=None):
        performance_logger.info(
            "api_request",
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration * 1000,
            query_count=query_count,
            user_id=request.user.id if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )
    
    @staticmethod
    def log_slow_query(query, duration, params=None):
        performance_logger.warning(
            "slow_query",
            query=query,
            duration_ms=duration * 1000,
            params=params
        )
    
    @staticmethod
    def log_cache_hit(key, hit=True):
        performance_logger.info(
            "cache_event",
            key=key,
            hit=hit
        )