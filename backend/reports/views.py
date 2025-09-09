from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Sum, Avg, Max, Min, F, Case, When, Value, CharField
from django.db.models.functions import TruncDate, TruncMonth, TruncYear, Extract
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from datetime import datetime, timedelta
import json
import csv
import io
from .models import Report, ReportTemplate, ReportSchedule
from .serializers import (
    ReportSerializer, ReportTemplateSerializer, ReportScheduleSerializer,
    ReportDataSerializer, CreateReportSerializer
)
from authentication.models import CustomUser
from common.models import Tag, TaggedItem, Mention, Notification
from customers.models import Customer
from products.models import Product
from invoices.models import Invoice
from inventory.models import InventoryItem

class ReportViewSet(viewsets.ModelViewSet):
    """مدیریت گزارش‌ها"""
    
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Report.objects.filter(
            Q(created_by=user) | Q(is_public=True)
        ).select_related('created_by', 'template').prefetch_related('tags')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateReportSerializer
        return ReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """اجرای گزارش"""
        report = self.get_object()
        
        # بررسی دسترسی
        if not self._has_report_permission(report, request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            data = self._execute_report(report, request.data.get('filters', {}))
            return Response({
                'report_id': report.id,
                'data': data,
                'executed_at': timezone.now(),
                'total_records': len(data) if isinstance(data, list) else 0
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def export(self, request, pk=None):
        """صادرات گزارش"""
        report = self.get_object()
        format_type = request.data.get('format', 'csv')
        
        if not self._has_report_permission(report, request.user):
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            data = self._execute_report(report, request.data.get('filters', {}))
            
            if format_type == 'csv':
                return self._export_csv(data, report.name)
            elif format_type == 'excel':
                return self._export_excel(data, report.name)
            elif format_type == 'json':
                return self._export_json(data, report.name)
            else:
                return Response({'error': 'Unsupported format'}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """آمار داشبورد"""
        user = self.request.user
        
        # فیلترهای اختیاری
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        tags = request.query_params.getlist('tags')
        responsible_user = request.query_params.get('responsible_user')
        province = request.query_params.get('province')
        
        stats = {}
        
        # آمار مشتریان
        customers_query = Customer.objects.all()
        if date_from:
            customers_query = customers_query.filter(created_at__gte=date_from)
        if date_to:
            customers_query = customers_query.filter(created_at__lte=date_to)
        if tags:
            customers_query = customers_query.filter(tags__name__in=tags)
        if province:
            customers_query = customers_query.filter(province=province)
        
        stats['customers'] = {
            'total': customers_query.count(),
            'active': customers_query.filter(status='active').count(),
            'inactive': customers_query.filter(status='inactive').count(),
            'by_type': list(customers_query.values('customer_type').annotate(count=Count('id'))),
            'by_province': list(customers_query.values('province').annotate(count=Count('id'))),
        }
        
        # آمار فاکتورها
        invoices_query = Invoice.objects.all()
        if date_from:
            invoices_query = invoices_query.filter(created_at__gte=date_from)
        if date_to:
            invoices_query = invoices_query.filter(created_at__lte=date_to)
        if responsible_user:
            invoices_query = invoices_query.filter(created_by_id=responsible_user)
        
        stats['invoices'] = {
            'total': invoices_query.count(),
            'total_amount': invoices_query.aggregate(total=Sum('total_amount'))['total'] or 0,
            'paid': invoices_query.filter(status='paid').count(),
            'pending': invoices_query.filter(status='pending').count(),
            'by_month': list(invoices_query.annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                count=Count('id'),
                total=Sum('total_amount')
            ).order_by('month')),
        }
        
        # آمار محصولات
        products_query = Product.objects.all()
        if tags:
            products_query = products_query.filter(tags__name__in=tags)
        
        stats['products'] = {
            'total': products_query.count(),
            'active': products_query.filter(is_active=True).count(),
            'low_stock': products_query.filter(stock_quantity__lt=F('min_stock_level')).count(),
            'by_category': list(products_query.values('category__name').annotate(count=Count('id'))),
        }
        
        # آمار انبار
        inventory_query = InventoryItem.objects.all()
        if date_from:
            inventory_query = inventory_query.filter(created_at__gte=date_from)
        if date_to:
            inventory_query = inventory_query.filter(created_at__lte=date_to)
        
        stats['inventory'] = {
            'total_items': inventory_query.count(),
            'total_value': inventory_query.aggregate(total=Sum(F('quantity') * F('unit_price')))['total'] or 0,
            'low_stock_items': inventory_query.filter(quantity__lt=F('min_quantity')).count(),
        }
        
        # آمار فعالیت‌ها
        activities_query = request.user.activities.all()
        if date_from:
            activities_query = activities_query.filter(created_at__gte=date_from)
        if date_to:
            activities_query = activities_query.filter(created_at__lte=date_to)
        
        stats['activities'] = {
            'total': activities_query.count(),
            'by_type': list(activities_query.values('activity_type').annotate(count=Count('id'))),
            'recent': list(activities_query.order_by('-created_at')[:10].values(
                'activity_type', 'description', 'created_at'
            )),
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def filter_options(self, request):
        """گزینه‌های فیلتر"""
        return Response({
            'tags': list(Tag.objects.filter(is_active=True).values('id', 'name', 'color', 'category')),
            'users': list(CustomUser.objects.filter(is_active=True).values('id', 'username', 'first_name', 'last_name')),
            'provinces': list(Customer.objects.values_list('province', flat=True).distinct().exclude(province__isnull=True)),
            'customer_types': Customer.CUSTOMER_TYPE_CHOICES,
            'invoice_statuses': Invoice.STATUS_CHOICES,
            'product_categories': list(Product.objects.values_list('category__name', flat=True).distinct().exclude(category__name__isnull=True)),
        })
    
    def _has_report_permission(self, report, user):
        """بررسی دسترسی به گزارش"""
        return report.created_by == user or report.is_public
    
    def _execute_report(self, report, filters):
        """اجرای گزارش"""
        template = report.template
        query = template.query
        
        # اعمال فیلترها
        if filters:
            query = self._apply_filters(query, filters)
        
        # اجرای کوئری
        # اینجا باید کوئری را به صورت امن اجرا کنیم
        # در عمل، باید از ORM استفاده کنیم
        
        return self._execute_safe_query(template, filters)
    
    def _apply_filters(self, query, filters):
        """اعمال فیلترها به کوئری"""
        # اینجا باید فیلترها را به کوئری اضافه کنیم
        # برای امنیت، باید از ORM استفاده کنیم
        pass
    
    def _execute_safe_query(self, template, filters):
        """اجرای امن کوئری"""
        # نمونه کوئری‌های امن
        if template.name == 'customers_report':
            return self._get_customers_data(filters)
        elif template.name == 'invoices_report':
            return self._get_invoices_data(filters)
        elif template.name == 'products_report':
            return self._get_products_data(filters)
        else:
            return []
    
    def _get_customers_data(self, filters):
        """داده‌های مشتریان"""
        query = Customer.objects.select_related('created_by').prefetch_related('tags')
        
        # اعمال فیلترها
        if filters.get('date_from'):
            query = query.filter(created_at__gte=filters['date_from'])
        if filters.get('date_to'):
            query = query.filter(created_at__lte=filters['date_to'])
        if filters.get('tags'):
            query = query.filter(tags__name__in=filters['tags'])
        if filters.get('responsible_user'):
            query = query.filter(created_by_id=filters['responsible_user'])
        if filters.get('province'):
            query = query.filter(province=filters['province'])
        if filters.get('status'):
            query = query.filter(status=filters['status'])
        
        return list(query.values(
            'id', 'first_name', 'last_name', 'company_name', 'email', 'phone_number',
            'province', 'city', 'status', 'customer_type', 'created_at',
            'created_by__first_name', 'created_by__last_name'
        ))
    
    def _get_invoices_data(self, filters):
        """داده‌های فاکتورها"""
        query = Invoice.objects.select_related('customer', 'created_by').prefetch_related('items')
        
        # اعمال فیلترها
        if filters.get('date_from'):
            query = query.filter(created_at__gte=filters['date_from'])
        if filters.get('date_to'):
            query = query.filter(created_at__lte=filters['date_to'])
        if filters.get('responsible_user'):
            query = query.filter(created_by_id=filters['responsible_user'])
        if filters.get('status'):
            query = query.filter(status=filters['status'])
        if filters.get('customer_id'):
            query = query.filter(customer_id=filters['customer_id'])
        
        return list(query.values(
            'id', 'invoice_number', 'customer__first_name', 'customer__last_name',
            'total_amount', 'status', 'created_at', 'created_by__first_name', 'created_by__last_name'
        ))
    
    def _get_products_data(self, filters):
        """داده‌های محصولات"""
        query = Product.objects.select_related('category').prefetch_related('tags')
        
        # اعمال فیلترها
        if filters.get('tags'):
            query = query.filter(tags__name__in=filters['tags'])
        if filters.get('category'):
            query = query.filter(category__name=filters['category'])
        if filters.get('is_active') is not None:
            query = query.filter(is_active=filters['is_active'])
        
        return list(query.values(
            'id', 'name', 'sku', 'category__name', 'price', 'stock_quantity',
            'min_stock_level', 'is_active', 'created_at'
        ))
    
    def _export_csv(self, data, filename):
        """صادرات CSV"""
        response = Response(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        if data:
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return response
    
    def _export_excel(self, data, filename):
        """صادرات Excel"""
        # TODO: پیاده‌سازی صادرات Excel
        return Response({'message': 'Excel export not implemented yet'})
    
    def _export_json(self, data, filename):
        """صادرات JSON"""
        response = Response(data, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
        return response

class ReportTemplateViewSet(viewsets.ModelViewSet):
    """مدیریت قالب‌های گزارش"""
    
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReportTemplate.objects.filter(
            Q(is_public=True) | Q(created_by=self.request.user)
        ).select_related('created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """کپی کردن قالب گزارش"""
        template = self.get_object()
        
        new_template = ReportTemplate.objects.create(
            name=f"{template.name} (Copy)",
            description=template.description,
            query=template.query,
            parameters=template.parameters,
            created_by=request.user,
            is_public=False
        )
        
        serializer = self.get_serializer(new_template)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReportScheduleViewSet(viewsets.ModelViewSet):
    """مدیریت زمان‌بندی گزارش‌ها"""
    
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReportSchedule.objects.filter(created_by=self.request.user).select_related('report', 'created_by')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """تست زمان‌بندی"""
        schedule = self.get_object()
        
        # TODO: پیاده‌سازی تست زمان‌بندی
        return Response({'message': 'Schedule test not implemented yet'})