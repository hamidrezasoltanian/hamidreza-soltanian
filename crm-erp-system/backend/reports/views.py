from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from .models import ReportTemplate, ReportExecution, ReportSchedule, Dashboard, DashboardWidget
from .serializers import (
    ReportTemplateSerializer, ReportExecutionSerializer, ReportScheduleSerializer,
    DashboardSerializer, DashboardWidgetSerializer
)


class ReportTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار قالب‌های گزارش"""
        total_templates = self.get_queryset().count()
        active_templates = self.get_queryset().filter(status='active').count()
        
        type_stats = {}
        for report_type, _ in ReportTemplate.REPORT_TYPES:
            type_stats[report_type] = self.get_queryset().filter(report_type=report_type).count()
        
        return Response({
            'total_templates': total_templates,
            'active_templates': active_templates,
            'type_stats': type_stats,
        })
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """اجرای قالب گزارش"""
        template = self.get_object()
        
        if template.status != 'active':
            return Response({'error': 'فقط قالب‌های فعال قابل اجرا هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # ایجاد اجرای گزارش
        execution = ReportExecution.objects.create(
            template=template,
            parameters=request.data.get('parameters', {}),
            status='running',
            created_by=request.user
        )
        
        # اجرای گزارش (در اینجا فقط وضعیت را تغییر می‌دهیم)
        execution.status = 'completed'
        execution.completed_at = timezone.now()
        execution.save()
        
        return Response({
            'message': 'گزارش با موفقیت اجرا شد',
            'execution_id': execution.id
        })


class ReportExecutionViewSet(viewsets.ModelViewSet):
    queryset = ReportExecution.objects.all()
    serializer_class = ReportExecutionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['template', 'status']
    ordering_fields = ['created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار اجرای گزارش‌ها"""
        total_executions = self.get_queryset().count()
        completed_executions = self.get_queryset().filter(status='completed').count()
        running_executions = self.get_queryset().filter(status='running').count()
        failed_executions = self.get_queryset().filter(status='failed').count()
        
        return Response({
            'total_executions': total_executions,
            'completed_executions': completed_executions,
            'running_executions': running_executions,
            'failed_executions': failed_executions,
        })


class ReportScheduleViewSet(viewsets.ModelViewSet):
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['template', 'frequency', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'next_run']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار برنامه‌های گزارش"""
        total_schedules = self.get_queryset().count()
        active_schedules = self.get_queryset().filter(status='active').count()
        
        frequency_stats = {}
        for frequency, _ in ReportSchedule.FREQUENCY_CHOICES:
            frequency_stats[frequency] = self.get_queryset().filter(frequency=frequency).count()
        
        return Response({
            'total_schedules': total_schedules,
            'active_schedules': active_schedules,
            'frequency_stats': frequency_stats,
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """فعال کردن برنامه گزارش"""
        schedule = self.get_object()
        
        if schedule.status == 'active':
            return Response({'error': 'برنامه گزارش قبلاً فعال است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'active'
        schedule.save()
        
        return Response({'message': 'برنامه گزارش با موفقیت فعال شد'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """غیرفعال کردن برنامه گزارش"""
        schedule = self.get_object()
        
        if schedule.status == 'inactive':
            return Response({'error': 'برنامه گزارش قبلاً غیرفعال است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        schedule.status = 'inactive'
        schedule.save()
        
        return Response({'message': 'برنامه گزارش با موفقیت غیرفعال شد'})


class DashboardViewSet(viewsets.ModelViewSet):
    queryset = Dashboard.objects.all()
    serializer_class = DashboardSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس دسترسی
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(is_public=True) | Q(created_by=self.request.user)
            )
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار داشبوردها"""
        total_dashboards = self.get_queryset().count()
        public_dashboards = self.get_queryset().filter(is_public=True).count()
        private_dashboards = total_dashboards - public_dashboards
        
        return Response({
            'total_dashboards': total_dashboards,
            'public_dashboards': public_dashboards,
            'private_dashboards': private_dashboards,
        })


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dashboard', 'widget_type']
    ordering_fields = ['position_x', 'position_y', 'created_at']
    ordering = ['dashboard', 'position_y', 'position_x']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس داشبورد
        dashboard_id = self.request.query_params.get('dashboard_id')
        if dashboard_id:
            queryset = queryset.filter(dashboard_id=dashboard_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار ویجت‌ها"""
        total_widgets = self.get_queryset().count()
        
        type_stats = {}
        for widget_type, _ in DashboardWidget.WIDGET_TYPES:
            type_stats[widget_type] = self.get_queryset().filter(widget_type=widget_type).count()
        
        return Response({
            'total_widgets': total_widgets,
            'type_stats': type_stats,
        })