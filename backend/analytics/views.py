from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import AnalyticsEvent, Report, BusinessMetric
from .serializers import ReportSerializer, BusinessMetricSerializer
from .services import AnalyticsService, ReportGenerator
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class AnalyticsViewSet(viewsets.ViewSet):
    """Analytics and reporting endpoints"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.analytics_service = AnalyticsService()
        self.report_generator = ReportGenerator()
    
    @action(detail=False, methods=['get'])
    def dashboard_summary(self, request):
        """Get comprehensive dashboard summary"""
        try:
            days = int(request.query_params.get('days', 30))
            summary = self.analytics_service.get_dashboard_summary(days)
            return Response(summary)
        except Exception as e:
            logger.error(f"Error getting dashboard summary: {str(e)}")
            return Response(
                {'error': 'Failed to get dashboard summary'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """Get user activity metrics"""
        try:
            days = int(request.query_params.get('days', 30))
            metrics = self.analytics_service.get_user_activity_metrics(days)
            return Response(metrics)
        except Exception as e:
            logger.error(f"Error getting user activity: {str(e)}")
            return Response(
                {'error': 'Failed to get user activity'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def sales_metrics(self, request):
        """Get sales performance metrics"""
        try:
            days = int(request.query_params.get('days', 30))
            metrics = self.analytics_service.get_sales_metrics(days)
            return Response(metrics)
        except Exception as e:
            logger.error(f"Error getting sales metrics: {str(e)}")
            return Response(
                {'error': 'Failed to get sales metrics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def customer_analytics(self, request):
        """Get customer analytics"""
        try:
            days = int(request.query_params.get('days', 30))
            analytics = self.analytics_service.get_customer_analytics(days)
            return Response(analytics)
        except Exception as e:
            logger.error(f"Error getting customer analytics: {str(e)}")
            return Response(
                {'error': 'Failed to get customer analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def product_analytics(self, request):
        """Get product analytics"""
        try:
            days = int(request.query_params.get('days', 30))
            analytics = self.analytics_service.get_product_analytics(days)
            return Response(analytics)
        except Exception as e:
            logger.error(f"Error getting product analytics: {str(e)}")
            return Response(
                {'error': 'Failed to get product analytics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def performance_metrics(self, request):
        """Get system performance metrics"""
        try:
            days = int(request.query_params.get('days', 7))
            metrics = self.analytics_service.get_system_performance_metrics(days)
            return Response(metrics)
        except Exception as e:
            logger.error(f"Error getting performance metrics: {str(e)}")
            return Response(
                {'error': 'Failed to get performance metrics'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def track_event(self, request):
        """Track a custom event"""
        try:
            event_type = request.data.get('event_type')
            event_name = request.data.get('event_name')
            properties = request.data.get('properties', {})
            content_object_id = request.data.get('content_object_id')
            content_type = request.data.get('content_type')
            
            if not event_type or not event_name:
                return Response(
                    {'error': 'event_type and event_name are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            content_object = None
            if content_object_id and content_type:
                from django.contrib.contenttypes.models import ContentType
                try:
                    ct = ContentType.objects.get(model=content_type)
                    content_object = ct.get_object_for_this_type(id=content_object_id)
                except:
                    pass
            
            event = self.analytics_service.track_event(
                user=request.user,
                event_type=event_type,
                event_name=event_name,
                properties=properties,
                content_object=content_object
            )
            
            if event:
                return Response({'message': 'Event tracked successfully'})
            else:
                return Response(
                    {'error': 'Failed to track event'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error tracking event: {str(e)}")
            return Response(
                {'error': 'Failed to track event'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def events(self, request):
        """Get recent events"""
        try:
            event_type = request.query_params.get('event_type')
            limit = int(request.query_params.get('limit', 100))
            
            events = AnalyticsEvent.objects.all()
            
            if event_type:
                events = events.filter(event_type=event_type)
            
            events = events.order_by('-timestamp')[:limit]
            
            data = []
            for event in events:
                data.append({
                    'id': event.id,
                    'event_type': event.event_type,
                    'event_name': event.event_name,
                    'user': event.user.username if event.user else 'Anonymous',
                    'timestamp': event.timestamp.isoformat(),
                    'properties': event.properties
                })
            
            return Response(data)
        except Exception as e:
            logger.error(f"Error getting events: {str(e)}")
            return Response(
                {'error': 'Failed to get events'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReportViewSet(viewsets.ModelViewSet):
    """Report management"""
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.filter(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate a report"""
        try:
            report = self.get_object()
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            
            if not start_date or not end_date:
                return Response(
                    {'error': 'start_date and end_date are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Parse dates
            from datetime import datetime
            start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Generate report based on type
            if report.report_type == 'user_activity':
                data = self.report_generator.generate_user_activity_report(
                    start_date, end_date
                )
            elif report.report_type == 'sales_performance':
                data = self.report_generator.generate_sales_report(
                    start_date, end_date
                )
            else:
                return Response(
                    {'error': 'Unsupported report type'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update report with generated data
            report.data = data
            report.last_generated = timezone.now()
            report.save()
            
            return Response(data)
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return Response(
                {'error': 'Failed to generate report'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available report templates"""
        templates = [
            {
                'type': 'user_activity',
                'name': 'User Activity Report',
                'description': 'Detailed user activity and engagement metrics',
                'parameters': ['start_date', 'end_date', 'user_id']
            },
            {
                'type': 'sales_performance',
                'name': 'Sales Performance Report',
                'description': 'Revenue, conversion rates, and sales trends',
                'parameters': ['start_date', 'end_date']
            },
            {
                'type': 'customer_analytics',
                'name': 'Customer Analytics Report',
                'description': 'Customer growth, demographics, and behavior',
                'parameters': ['start_date', 'end_date']
            },
            {
                'type': 'product_analytics',
                'name': 'Product Analytics Report',
                'description': 'Product performance and popularity metrics',
                'parameters': ['start_date', 'end_date']
            },
            {
                'type': 'system_performance',
                'name': 'System Performance Report',
                'description': 'API performance, database metrics, and system health',
                'parameters': ['start_date', 'end_date']
            }
        ]
        
        return Response(templates)


class BusinessMetricViewSet(viewsets.ModelViewSet):
    """Business metrics management"""
    queryset = BusinessMetric.objects.all()
    serializer_class = BusinessMetricSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get metric trends"""
        try:
            metric_type = request.query_params.get('metric_type')
            days = int(request.query_params.get('days', 30))
            
            start_date = timezone.now() - timedelta(days=days)
            
            metrics = BusinessMetric.objects.filter(
                period_start__gte=start_date
            )
            
            if metric_type:
                metrics = metrics.filter(metric_type=metric_type)
            
            metrics = metrics.order_by('period_start')
            
            data = []
            for metric in metrics:
                data.append({
                    'date': metric.period_start.isoformat(),
                    'value': float(metric.value),
                    'metric_type': metric.metric_type
                })
            
            return Response(data)
            
        except Exception as e:
            logger.error(f"Error getting trends: {str(e)}")
            return Response(
                {'error': 'Failed to get trends'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )