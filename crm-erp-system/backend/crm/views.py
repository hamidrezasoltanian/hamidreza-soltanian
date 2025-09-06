from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from .models import SalesProcess, ProcessStage, ProcessActivity, Lead, Task
from .serializers import (
    SalesProcessSerializer, SalesProcessListSerializer, ProcessStageSerializer,
    ProcessActivitySerializer, LeadSerializer, LeadListSerializer,
    TaskSerializer, TaskListSerializer
)


class SalesProcessViewSet(viewsets.ModelViewSet):
    queryset = SalesProcess.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'process_type', 'priority', 'assigned_to']
    search_fields = ['process_name', 'description', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['start_date', 'expected_close_date', 'estimated_value', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SalesProcessListSerializer
        return SalesProcessSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(start_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(start_date__lte=date_to)
        
        # فیلتر بر اساس مقدار
        min_value = self.request.query_params.get('min_value')
        max_value = self.request.query_params.get('max_value')
        
        if min_value:
            queryset = queryset.filter(estimated_value__gte=min_value)
        if max_value:
            queryset = queryset.filter(estimated_value__lte=max_value)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی فرایندهای فروش"""
        total_processes = self.get_queryset().count()
        total_value = self.get_queryset().aggregate(total=Sum('estimated_value'))['total'] or 0
        weighted_value = self.get_queryset().aggregate(total=Sum('weighted_value'))['total'] or 0
        
        type_stats = {}
        for process_type, _ in SalesProcess.PROCESS_TYPES:
            type_stats[process_type] = self.get_queryset().filter(process_type=process_type).count()
        
        priority_stats = {}
        for priority, _ in SalesProcess.PRIORITY_LEVELS:
            priority_stats[priority] = self.get_queryset().filter(priority=priority).count()
        
        return Response({
            'total_processes': total_processes,
            'total_value': total_value,
            'weighted_value': weighted_value,
            'type_stats': type_stats,
            'priority_stats': priority_stats,
        })
    
    @action(detail=True, methods=['post'])
    def add_stage(self, request, pk=None):
        """اضافه کردن مرحله"""
        process = self.get_object()
        stage_data = request.data.copy()
        stage_data['process'] = process.id
        
        serializer = ProcessStageSerializer(data=stage_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_activity(self, request, pk=None):
        """اضافه کردن فعالیت"""
        process = self.get_object()
        activity_data = request.data.copy()
        activity_data['process'] = process.id
        
        serializer = ProcessActivitySerializer(data=activity_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def close_won(self, request, pk=None):
        """بستن فرایند به عنوان موفق"""
        process = self.get_object()
        
        if process.process_type in ['closed_won', 'closed_lost']:
            return Response({'error': 'فرایند قبلاً بسته شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        process.process_type = 'closed_won'
        process.actual_close_date = timezone.now().date()
        process.actual_value = request.data.get('actual_value', process.estimated_value)
        process.save()
        
        return Response({'message': 'فرایند با موفقیت بسته شد'})
    
    @action(detail=True, methods=['post'])
    def close_lost(self, request, pk=None):
        """بستن فرایند به عنوان ناموفق"""
        process = self.get_object()
        
        if process.process_type in ['closed_won', 'closed_lost']:
            return Response({'error': 'فرایند قبلاً بسته شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        process.process_type = 'closed_lost'
        process.actual_close_date = timezone.now().date()
        process.save()
        
        return Response({'message': 'فرایند به عنوان ناموفق بسته شد'})


class ProcessStageViewSet(viewsets.ModelViewSet):
    queryset = ProcessStage.objects.all()
    serializer_class = ProcessStageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['process', 'is_completed']
    ordering_fields = ['stage_order', 'completed_at']
    ordering = ['process', 'stage_order']
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """تکمیل مرحله"""
        stage = self.get_object()
        
        if stage.is_completed:
            return Response({'error': 'مرحله قبلاً تکمیل شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        stage.is_completed = True
        stage.completed_at = timezone.now()
        stage.completed_by = request.user
        stage.save()
        
        return Response({'message': 'مرحله با موفقیت تکمیل شد'})


class ProcessActivityViewSet(viewsets.ModelViewSet):
    queryset = ProcessActivity.objects.all()
    serializer_class = ProcessActivitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['process', 'activity_type', 'created_by']
    search_fields = ['subject', 'description']
    ordering_fields = ['activity_date', 'duration']
    ordering = ['-activity_date']


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source', 'status', 'assigned_to', 'industry']
    search_fields = ['lead_name', 'company_name', 'contact_person', 'email', 'phone']
    ordering_fields = ['created_at', 'estimated_value']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # فیلتر بر اساس مقدار
        min_value = self.request.query_params.get('min_value')
        max_value = self.request.query_params.get('max_value')
        
        if min_value:
            queryset = queryset.filter(estimated_value__gte=min_value)
        if max_value:
            queryset = queryset.filter(estimated_value__lte=max_value)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی سرنخ‌ها"""
        total_leads = self.get_queryset().count()
        total_value = self.get_queryset().aggregate(total=Sum('estimated_value'))['total'] or 0
        converted_leads = self.get_queryset().filter(status='converted').count()
        
        source_stats = {}
        for source, _ in Lead.LEAD_SOURCES:
            source_stats[source] = self.get_queryset().filter(source=source).count()
        
        status_stats = {}
        for status, _ in Lead.STATUS_CHOICES:
            status_stats[status] = self.get_queryset().filter(status=status).count()
        
        return Response({
            'total_leads': total_leads,
            'total_value': total_value,
            'converted_leads': converted_leads,
            'source_stats': source_stats,
            'status_stats': status_stats,
        })
    
    @action(detail=True, methods=['post'])
    def convert_to_customer(self, request, pk=None):
        """تبدیل سرنخ به مشتری"""
        lead = self.get_object()
        
        if lead.status == 'converted':
            return Response({'error': 'سرنخ قبلاً تبدیل شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # ایجاد مشتری جدید
        from customers.models import Customer
        
        customer = Customer.objects.create(
            customer_code=f"CUST-{lead.id}",
            customer_type='legal' if lead.company_name else 'individual',
            first_name=lead.contact_person.split(' ')[0] if lead.contact_person else lead.lead_name,
            last_name=' '.join(lead.contact_person.split(' ')[1:]) if lead.contact_person and ' ' in lead.contact_person else '',
            company_name=lead.company_name,
            phone_number=lead.phone or '',
            email=lead.email,
            address='',
            postal_code='',
            city='',
            state='',
            created_by=request.user
        )
        
        # بروزرسانی وضعیت سرنخ
        lead.status = 'converted'
        lead.converted_to_customer = customer
        lead.converted_at = timezone.now()
        lead.save()
        
        return Response({
            'message': 'سرنخ با موفقیت به مشتری تبدیل شد',
            'customer_id': customer.id,
            'customer_code': customer.customer_code
        })


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'status', 'assigned_to', 'reference_type']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # فیلتر بر اساس سررسید
        due_soon = self.request.query_params.get('due_soon')
        if due_soon:
            from datetime import timedelta
            future_date = timezone.now() + timedelta(days=int(due_soon))
            queryset = queryset.filter(due_date__lte=future_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی وظایف"""
        total_tasks = self.get_queryset().count()
        completed_tasks = self.get_queryset().filter(status='completed').count()
        pending_tasks = self.get_queryset().filter(status='pending').count()
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        priority_stats = {}
        for priority, _ in Task.PRIORITY_LEVELS:
            priority_stats[priority] = self.get_queryset().filter(priority=priority).count()
        
        status_stats = {}
        for status, _ in Task.STATUS_CHOICES:
            status_stats[status] = self.get_queryset().filter(status=status).count()
        
        return Response({
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'pending_tasks': pending_tasks,
            'overdue_tasks': overdue_tasks,
            'priority_stats': priority_stats,
            'status_stats': status_stats,
        })
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """تکمیل وظیفه"""
        task = self.get_object()
        
        if task.status == 'completed':
            return Response({'error': 'وظیفه قبلاً تکمیل شده است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        task.status = 'completed'
        task.completed_at = timezone.now()
        task.save()
        
        return Response({'message': 'وظیفه با موفقیت تکمیل شد'})
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """شروع وظیفه"""
        task = self.get_object()
        
        if task.status != 'pending':
            return Response({'error': 'فقط وظایف در انتظار قابل شروع هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        task.status = 'in_progress'
        task.save()
        
        return Response({'message': 'وظیفه شروع شد'})