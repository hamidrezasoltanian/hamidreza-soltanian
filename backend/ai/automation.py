from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from customers.models import Customer
from invoices.models import Invoice
from products.models import Product
from analytics.models import AnalyticsEvent
from notifications.models import Notification
from .recommendation_engine import RecommendationEngine
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class SmartAutomation:
    """AI-powered automation system"""
    
    def __init__(self):
        self.recommendation_engine = RecommendationEngine()
    
    def run_automated_tasks(self):
        """Run all automated tasks"""
        try:
            logger.info("Starting automated tasks...")
            
            # Run different automation tasks
            self._automate_customer_segmentation()
            self._automate_invoice_follow_up()
            self._automate_inventory_alerts()
            self._automate_customer_engagement()
            self._automate_sales_opportunities()
            self._automate_system_optimization()
            
            logger.info("Automated tasks completed successfully")
            
        except Exception as e:
            logger.error(f"Error running automated tasks: {str(e)}")
    
    def _automate_customer_segmentation(self):
        """Automatically segment customers and create targeted campaigns"""
        try:
            logger.info("Running customer segmentation automation...")
            
            # Get customer segments
            segments = self.recommendation_engine.get_customer_segments()
            
            for segment in segments:
                # Create notification for sales team
                self._create_automation_notification(
                    title=f"بخش‌بندی مشتریان: {segment['name']}",
                    message=f"تعداد مشتریان: {segment['customer_count']}, میانگین خرید: {segment['metrics']['avg_invoice_value']:,.0f}",
                    notification_type="customer_segmentation",
                    data={
                        'segment_id': segment['id'],
                        'segment_name': segment['name'],
                        'customer_count': segment['customer_count'],
                        'metrics': segment['metrics']
                    }
                )
            
            logger.info(f"Customer segmentation completed: {len(segments)} segments created")
            
        except Exception as e:
            logger.error(f"Error in customer segmentation automation: {str(e)}")
    
    def _automate_invoice_follow_up(self):
        """Automatically follow up on overdue invoices"""
        try:
            logger.info("Running invoice follow-up automation...")
            
            # Find overdue invoices
            overdue_threshold = timezone.now() - timedelta(days=30)
            overdue_invoices = Invoice.objects.filter(
                status='pending',
                due_date__lt=overdue_threshold
            ).select_related('customer')
            
            for invoice in overdue_invoices:
                # Calculate days overdue
                days_overdue = (timezone.now().date() - invoice.due_date).days
                
                # Create follow-up notification
                self._create_automation_notification(
                    title="فاکتور معوق",
                    message=f"فاکتور {invoice.invoice_number} مشتری {invoice.customer.get_full_name()} {days_overdue} روز معوق است",
                    notification_type="overdue_invoice",
                    data={
                        'invoice_id': invoice.id,
                        'invoice_number': invoice.invoice_number,
                        'customer_name': invoice.customer.get_full_name(),
                        'amount': float(invoice.total_amount),
                        'days_overdue': days_overdue
                    }
                )
                
                # Send email reminder (if configured)
                self._send_email_reminder(invoice, days_overdue)
            
            logger.info(f"Invoice follow-up completed: {overdue_invoices.count()} overdue invoices processed")
            
        except Exception as e:
            logger.error(f"Error in invoice follow-up automation: {str(e)}")
    
    def _automate_inventory_alerts(self):
        """Automatically alert on low inventory levels"""
        try:
            logger.info("Running inventory alerts automation...")
            
            # Find products with low stock
            low_stock_products = Product.objects.filter(
                status='active',
                stock_quantity__lt=10  # Assuming 10 is the low stock threshold
            )
            
            for product in low_stock_products:
                # Create inventory alert
                self._create_automation_notification(
                    title="موجودی کم",
                    message=f"محصول {product.name} موجودی کمی دارد ({product.stock_quantity} عدد)",
                    notification_type="low_inventory",
                    data={
                        'product_id': product.id,
                        'product_name': product.name,
                        'current_stock': product.stock_quantity,
                        'category': product.category.name if product.category else None
                    }
                )
            
            # Find products with no recent sales
            no_sales_threshold = timezone.now() - timedelta(days=90)
            stagnant_products = Product.objects.filter(
                status='active',
                created_at__lt=no_sales_threshold
            ).exclude(
                id__in=Invoice.objects.filter(
                    items__product__isnull=False,
                    created_at__gte=no_sales_threshold
                ).values_list('items__product', flat=True)
            )
            
            for product in stagnant_products:
                self._create_automation_notification(
                    title="محصول بدون فروش",
                    message=f"محصول {product.name} در 90 روز گذشته فروشی نداشته است",
                    notification_type="stagnant_product",
                    data={
                        'product_id': product.id,
                        'product_name': product.name,
                        'days_without_sales': 90
                    }
                )
            
            logger.info(f"Inventory alerts completed: {low_stock_products.count()} low stock, {stagnant_products.count()} stagnant products")
            
        except Exception as e:
            logger.error(f"Error in inventory alerts automation: {str(e)}")
    
    def _automate_customer_engagement(self):
        """Automatically engage with customers based on their behavior"""
        try:
            logger.info("Running customer engagement automation...")
            
            # Find customers who haven't made a purchase in 60 days
            inactive_threshold = timezone.now() - timedelta(days=60)
            inactive_customers = Customer.objects.filter(
                status='active',
                last_purchase_date__lt=inactive_threshold
            )
            
            for customer in inactive_customers:
                # Get personalized product recommendations
                recommendations = self.recommendation_engine.get_customer_recommendations(
                    customer.id, limit=3
                )
                
                if recommendations:
                    # Create re-engagement notification
                    self._create_automation_notification(
                        title="مشتری غیرفعال",
                        message=f"مشتری {customer.get_full_name()} در 60 روز گذشته خریدی نداشته است",
                        notification_type="inactive_customer",
                        data={
                            'customer_id': customer.id,
                            'customer_name': customer.get_full_name(),
                            'last_purchase_date': customer.last_purchase_date.isoformat() if customer.last_purchase_date else None,
                            'recommendations': recommendations
                        }
                    )
            
            # Find high-value customers for VIP treatment
            high_value_customers = Customer.objects.annotate(
                total_spent=Sum('invoice__total_amount', filter=Q(invoice__status='paid'))
            ).filter(
                total_spent__gte=1000000,  # 1M threshold
                status='active'
            )
            
            for customer in high_value_customers:
                self._create_automation_notification(
                    title="مشتری VIP",
                    message=f"مشتری {customer.get_full_name()} مشتری VIP است (مجموع خرید: {customer.total_spent:,.0f})",
                    notification_type="vip_customer",
                    data={
                        'customer_id': customer.id,
                        'customer_name': customer.get_full_name(),
                        'total_spent': float(customer.total_spent)
                    }
                )
            
            logger.info(f"Customer engagement completed: {inactive_customers.count()} inactive, {high_value_customers.count()} VIP customers")
            
        except Exception as e:
            logger.error(f"Error in customer engagement automation: {str(e)}")
    
    def _automate_sales_opportunities(self):
        """Automatically identify and create sales opportunities"""
        try:
            logger.info("Running sales opportunities automation...")
            
            # Find customers with increasing purchase frequency
            growing_customers = Customer.objects.annotate(
                recent_purchases=Count('invoice', filter=Q(
                    invoice__created_at__gte=timezone.now() - timedelta(days=30),
                    invoice__status='paid'
                )),
                previous_purchases=Count('invoice', filter=Q(
                    invoice__created_at__gte=timezone.now() - timedelta(days=60),
                    invoice__created_at__lt=timezone.now() - timedelta(days=30),
                    invoice__status='paid'
                ))
            ).filter(
                recent_purchases__gt=F('previous_purchases'),
                recent_purchases__gte=2
            )
            
            for customer in growing_customers:
                self._create_automation_notification(
                    title="فرصت فروش",
                    message=f"مشتری {customer.get_full_name()} در حال رشد است - فرصت فروش بیشتر",
                    notification_type="sales_opportunity",
                    data={
                        'customer_id': customer.id,
                        'customer_name': customer.get_full_name(),
                        'recent_purchases': customer.recent_purchases,
                        'previous_purchases': customer.previous_purchases
                    }
                )
            
            # Find customers with high cart abandonment
            # This would require tracking cart events, which we'll simulate
            cart_abandonment_customers = Customer.objects.filter(
                status='active'
            ).annotate(
                cart_events=Count('analytics_events', filter=Q(
                    analytics_events__event_type='cart_added'
                )),
                completed_purchases=Count('invoice', filter=Q(
                    invoice__status='paid'
                ))
            ).filter(
                cart_events__gt=F('completed_purchases') * 2,
                cart_events__gte=3
            )
            
            for customer in cart_abandonment_customers:
                self._create_automation_notification(
                    title="ترک سبد خرید",
                    message=f"مشتری {customer.get_full_name()} سبد خرید را رها کرده است - فرصت پیگیری",
                    notification_type="cart_abandonment",
                    data={
                        'customer_id': customer.id,
                        'customer_name': customer.get_full_name(),
                        'cart_events': customer.cart_events,
                        'completed_purchases': customer.completed_purchases
                    }
                )
            
            logger.info(f"Sales opportunities completed: {growing_customers.count()} growing, {cart_abandonment_customers.count()} cart abandonment customers")
            
        except Exception as e:
            logger.error(f"Error in sales opportunities automation: {str(e)}")
    
    def _automate_system_optimization(self):
        """Automatically optimize system performance and suggest improvements"""
        try:
            logger.info("Running system optimization automation...")
            
            # Analyze slow API endpoints
            from analytics.models import PerformanceMetric
            slow_endpoints = PerformanceMetric.objects.filter(
                metric_type='api_response_time',
                value__gt=1000,  # More than 1 second
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).values('endpoint').annotate(
                avg_response_time=Avg('value'),
                count=Count('id')
            ).order_by('-avg_response_time')
            
            for endpoint in slow_endpoints:
                self._create_automation_notification(
                    title="عملکرد کند API",
                    message=f"اندپوینت {endpoint['endpoint']} کند است (میانگین: {endpoint['avg_response_time']:.0f}ms)",
                    notification_type="slow_api",
                    data={
                        'endpoint': endpoint['endpoint'],
                        'avg_response_time': endpoint['avg_response_time'],
                        'count': endpoint['count']
                    }
                )
            
            # Analyze error rates
            error_events = AnalyticsEvent.objects.filter(
                event_type='api_call',
                properties__status_code__gte=400,
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).count()
            
            total_events = AnalyticsEvent.objects.filter(
                event_type='api_call',
                timestamp__gte=timezone.now() - timedelta(days=1)
            ).count()
            
            if total_events > 0:
                error_rate = (error_events / total_events) * 100
                if error_rate > 5:  # More than 5% error rate
                    self._create_automation_notification(
                        title="نرخ خطای بالا",
                        message=f"نرخ خطای سیستم {error_rate:.1f}% است - نیاز به بررسی",
                        notification_type="high_error_rate",
                        data={
                            'error_rate': error_rate,
                            'error_events': error_events,
                            'total_events': total_events
                        }
                    )
            
            logger.info("System optimization completed")
            
        except Exception as e:
            logger.error(f"Error in system optimization automation: {str(e)}")
    
    def _create_automation_notification(self, title: str, message: str, notification_type: str, data: Dict[str, Any]):
        """Create an automation notification"""
        try:
            # Get admin users
            from django.contrib.auth.models import User
            admin_users = User.objects.filter(is_staff=True)
            
            for user in admin_users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    data=data
                )
            
        except Exception as e:
            logger.error(f"Error creating automation notification: {str(e)}")
    
    def _send_email_reminder(self, invoice, days_overdue):
        """Send email reminder for overdue invoice"""
        try:
            # This would integrate with your email service
            # For now, just log the action
            logger.info(f"Email reminder sent for invoice {invoice.invoice_number} ({days_overdue} days overdue)")
            
        except Exception as e:
            logger.error(f"Error sending email reminder: {str(e)}")
    
    def get_automation_insights(self) -> Dict[str, Any]:
        """Get insights from automation system"""
        try:
            # Get recent automation notifications
            recent_notifications = Notification.objects.filter(
                notification_type__in=[
                    'customer_segmentation',
                    'overdue_invoice',
                    'low_inventory',
                    'inactive_customer',
                    'sales_opportunity',
                    'slow_api',
                    'high_error_rate'
                ],
                created_at__gte=timezone.now() - timedelta(days=7)
            ).values('notification_type').annotate(
                count=Count('id')
            )
            
            # Get automation statistics
            total_automations = sum(notif['count'] for notif in recent_notifications)
            
            insights = {
                'total_automations': total_automations,
                'automation_breakdown': list(recent_notifications),
                'last_run': timezone.now().isoformat(),
                'status': 'active'
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting automation insights: {str(e)}")
            return {'error': str(e)}