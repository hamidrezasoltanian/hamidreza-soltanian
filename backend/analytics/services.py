from django.db.models import Count, Sum, Avg, Q, F
from django.db.models.functions import TruncDate, TruncMonth, TruncYear
from django.utils import timezone
from datetime import timedelta, datetime
from .models import AnalyticsEvent, UserSession, PerformanceMetric, BusinessMetric
from customers.models import Customer
from invoices.models import Invoice
from products.models import Product
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for generating analytics and insights"""
    
    def __init__(self):
        self.now = timezone.now()
    
    def get_user_activity_metrics(self, days=30):
        """Get user activity metrics for the last N days"""
        start_date = self.now - timedelta(days=days)
        
        # Active users
        active_users = UserSession.objects.filter(
            start_time__gte=start_date
        ).values('user').distinct().count()
        
        # Total sessions
        total_sessions = UserSession.objects.filter(
            start_time__gte=start_date
        ).count()
        
        # Average session duration
        avg_session_duration = UserSession.objects.filter(
            start_time__gte=start_date,
            duration__isnull=False
        ).aggregate(
            avg_duration=Avg('duration')
        )['avg_duration']
        
        # Page views
        total_page_views = AnalyticsEvent.objects.filter(
            event_type='page_view',
            timestamp__gte=start_date
        ).count()
        
        # Most active users
        most_active_users = UserSession.objects.filter(
            start_time__gte=start_date
        ).values('user__username').annotate(
            session_count=Count('id')
        ).order_by('-session_count')[:10]
        
        return {
            'active_users': active_users,
            'total_sessions': total_sessions,
            'avg_session_duration': avg_session_duration.total_seconds() if avg_session_duration else 0,
            'total_page_views': total_page_views,
            'most_active_users': list(most_active_users)
        }
    
    def get_sales_metrics(self, days=30):
        """Get sales performance metrics"""
        start_date = self.now - timedelta(days=days)
        
        # Revenue metrics
        revenue_data = Invoice.objects.filter(
            created_at__gte=start_date,
            status='paid'
        ).aggregate(
            total_revenue=Sum('total_amount'),
            avg_invoice_value=Avg('total_amount'),
            invoice_count=Count('id')
        )
        
        # Revenue by day
        daily_revenue = Invoice.objects.filter(
            created_at__gte=start_date,
            status='paid'
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('date')
        
        # Top customers by revenue
        top_customers = Invoice.objects.filter(
            created_at__gte=start_date,
            status='paid'
        ).values(
            'customer__first_name',
            'customer__last_name',
            'customer__company_name'
        ).annotate(
            total_revenue=Sum('total_amount'),
            invoice_count=Count('id')
        ).order_by('-total_revenue')[:10]
        
        # Conversion rate (invoices created vs paid)
        total_invoices = Invoice.objects.filter(created_at__gte=start_date).count()
        paid_invoices = Invoice.objects.filter(
            created_at__gte=start_date,
            status='paid'
        ).count()
        
        conversion_rate = (paid_invoices / total_invoices * 100) if total_invoices > 0 else 0
        
        return {
            'total_revenue': revenue_data['total_revenue'] or 0,
            'avg_invoice_value': revenue_data['avg_invoice_value'] or 0,
            'invoice_count': revenue_data['invoice_count'],
            'conversion_rate': round(conversion_rate, 2),
            'daily_revenue': list(daily_revenue),
            'top_customers': list(top_customers)
        }
    
    def get_customer_analytics(self, days=30):
        """Get customer analytics"""
        start_date = self.now - timedelta(days=days)
        
        # Customer growth
        total_customers = Customer.objects.count()
        new_customers = Customer.objects.filter(created_at__gte=start_date).count()
        
        # Customer growth by day
        daily_customer_growth = Customer.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        # Customer types
        customer_types = Customer.objects.values('customer_type').annotate(
            count=Count('id')
        )
        
        # Customer status
        customer_status = Customer.objects.values('status').annotate(
            count=Count('id')
        )
        
        # Top cities
        top_cities = Customer.objects.exclude(
            city__isnull=True
        ).exclude(
            city=''
        ).values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Customer lifetime value (simplified)
        customer_lifetime_value = Invoice.objects.filter(
            status='paid'
        ).values('customer').annotate(
            total_revenue=Sum('total_amount'),
            invoice_count=Count('id')
        ).aggregate(
            avg_lifetime_value=Avg('total_revenue')
        )['avg_lifetime_value'] or 0
        
        return {
            'total_customers': total_customers,
            'new_customers': new_customers,
            'daily_growth': list(daily_customer_growth),
            'customer_types': list(customer_types),
            'customer_status': list(customer_status),
            'top_cities': list(top_cities),
            'avg_lifetime_value': customer_lifetime_value
        }
    
    def get_product_analytics(self, days=30):
        """Get product analytics"""
        start_date = self.now - timedelta(days=days)
        
        # Product metrics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        
        # Product views
        product_views = AnalyticsEvent.objects.filter(
            event_type='product_viewed',
            timestamp__gte=start_date
        ).count()
        
        # Most viewed products
        most_viewed_products = AnalyticsEvent.objects.filter(
            event_type='product_viewed',
            timestamp__gte=start_date
        ).values(
            'content_object__name',
            'content_object__category__name'
        ).annotate(
            view_count=Count('id')
        ).order_by('-view_count')[:10]
        
        # Product categories
        product_categories = Product.objects.values(
            'category__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        return {
            'total_products': total_products,
            'active_products': active_products,
            'product_views': product_views,
            'most_viewed_products': list(most_viewed_products),
            'product_categories': list(product_categories)
        }
    
    def get_system_performance_metrics(self, days=7):
        """Get system performance metrics"""
        start_date = self.now - timedelta(days=days)
        
        # API response times
        api_response_times = PerformanceMetric.objects.filter(
            metric_type='api_response_time',
            timestamp__gte=start_date
        ).aggregate(
            avg_response_time=Avg('value'),
            max_response_time=Max('value'),
            min_response_time=Min('value')
        )
        
        # Database query times
        db_query_times = PerformanceMetric.objects.filter(
            metric_type='database_query_time',
            timestamp__gte=start_date
        ).aggregate(
            avg_query_time=Avg('value'),
            max_query_time=Max('value')
        )
        
        # Cache hit rate
        cache_metrics = PerformanceMetric.objects.filter(
            metric_type='cache_hit_rate',
            timestamp__gte=start_date
        ).aggregate(
            avg_hit_rate=Avg('value')
        )
        
        # Error rates
        error_events = AnalyticsEvent.objects.filter(
            event_type='api_call',
            timestamp__gte=start_date,
            properties__status_code__gte=400
        ).count()
        
        total_api_calls = AnalyticsEvent.objects.filter(
            event_type='api_call',
            timestamp__gte=start_date
        ).count()
        
        error_rate = (error_events / total_api_calls * 100) if total_api_calls > 0 else 0
        
        return {
            'avg_api_response_time': api_response_times['avg_response_time'] or 0,
            'max_api_response_time': api_response_times['max_response_time'] or 0,
            'avg_db_query_time': db_query_times['avg_query_time'] or 0,
            'max_db_query_time': db_query_times['max_query_time'] or 0,
            'cache_hit_rate': cache_metrics['avg_hit_rate'] or 0,
            'error_rate': round(error_rate, 2)
        }
    
    def get_dashboard_summary(self, days=30):
        """Get comprehensive dashboard summary"""
        return {
            'user_activity': self.get_user_activity_metrics(days),
            'sales': self.get_sales_metrics(days),
            'customers': self.get_customer_analytics(days),
            'products': self.get_product_analytics(days),
            'performance': self.get_system_performance_metrics(7)
        }
    
    def track_event(self, user, event_type, event_name, properties=None, content_object=None):
        """Track a custom event"""
        try:
            event = AnalyticsEvent.objects.create(
                user=user,
                session_id=getattr(user, 'session_id', ''),
                event_type=event_type,
                event_name=event_name,
                properties=properties or {},
                content_object=content_object
            )
            return event
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return None
    
    def generate_trend_data(self, metric_type, days=30, group_by='day'):
        """Generate trend data for a specific metric"""
        start_date = self.now - timedelta(days=days)
        
        if group_by == 'day':
            trunc_func = TruncDate
        elif group_by == 'month':
            trunc_func = TruncMonth
        elif group_by == 'year':
            trunc_func = TruncYear
        else:
            trunc_func = TruncDate
        
        # This would need to be customized based on the metric type
        # For now, return a placeholder
        return {
            'labels': [],
            'data': []
        }


class ReportGenerator:
    """Generate various types of reports"""
    
    def __init__(self):
        self.analytics_service = AnalyticsService()
    
    def generate_user_activity_report(self, start_date, end_date, user_id=None):
        """Generate user activity report"""
        events = AnalyticsEvent.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        )
        
        if user_id:
            events = events.filter(user_id=user_id)
        
        # Group by event type
        event_summary = events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Group by user
        user_summary = events.values(
            'user__username'
        ).annotate(
            event_count=Count('id')
        ).order_by('-event_count')
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_events': events.count(),
            'event_summary': list(event_summary),
            'user_summary': list(user_summary)
        }
    
    def generate_sales_report(self, start_date, end_date):
        """Generate sales report"""
        invoices = Invoice.objects.filter(
            created_at__gte=start_date,
            created_at__lte=end_date
        )
        
        # Revenue by status
        revenue_by_status = invoices.values('status').annotate(
            total_revenue=Sum('total_amount'),
            count=Count('id')
        )
        
        # Revenue by month
        monthly_revenue = invoices.annotate(
            month=TruncMonth('created_at')
        ).values('month').annotate(
            revenue=Sum('total_amount'),
            count=Count('id')
        ).order_by('month')
        
        # Top customers
        top_customers = invoices.values(
            'customer__first_name',
            'customer__last_name',
            'customer__company_name'
        ).annotate(
            total_revenue=Sum('total_amount'),
            invoice_count=Count('id')
        ).order_by('-total_revenue')[:20]
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'total_revenue': invoices.aggregate(
                total=Sum('total_amount')
            )['total'] or 0,
            'total_invoices': invoices.count(),
            'revenue_by_status': list(revenue_by_status),
            'monthly_revenue': list(monthly_revenue),
            'top_customers': list(top_customers)
        }