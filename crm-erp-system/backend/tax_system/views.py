from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from .models import TaxPayer, TaxRate, TaxTransaction
from .serializers import TaxPayerSerializer, TaxRateSerializer, TaxTransactionSerializer


class TaxPayerViewSet(viewsets.ModelViewSet):
    queryset = TaxPayer.objects.all()
    serializer_class = TaxPayerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['taxpayer_type', 'status']
    search_fields = ['taxpayer_id', 'name', 'economic_code', 'national_id']
    ordering_fields = ['name', 'created_at']
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
        """آمار مودیان مالیاتی"""
        total_taxpayers = self.get_queryset().count()
        active_taxpayers = self.get_queryset().filter(status='active').count()
        
        type_stats = {}
        for taxpayer_type, _ in TaxPayer.TAXPAYER_TYPES:
            type_stats[taxpayer_type] = self.get_queryset().filter(taxpayer_type=taxpayer_type).count()
        
        return Response({
            'total_taxpayers': total_taxpayers,
            'active_taxpayers': active_taxpayers,
            'type_stats': type_stats,
        })
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """فعال کردن مودی مالیاتی"""
        taxpayer = self.get_object()
        
        if taxpayer.status == 'active':
            return Response({'error': 'مودی مالیاتی قبلاً فعال است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        taxpayer.status = 'active'
        taxpayer.save()
        
        return Response({'message': 'مودی مالیاتی با موفقیت فعال شد'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """غیرفعال کردن مودی مالیاتی"""
        taxpayer = self.get_object()
        
        if taxpayer.status == 'inactive':
            return Response({'error': 'مودی مالیاتی قبلاً غیرفعال است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        taxpayer.status = 'inactive'
        taxpayer.save()
        
        return Response({'message': 'مودی مالیاتی با موفقیت غیرفعال شد'})


class TaxRateViewSet(viewsets.ModelViewSet):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tax_type', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'rate', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(effective_from__gte=date_from)
        if date_to:
            queryset = queryset.filter(effective_from__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """نرخ‌های مالیاتی فعال"""
        active_rates = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_rates, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار نرخ‌های مالیاتی"""
        total_rates = self.get_queryset().count()
        active_rates = self.get_queryset().filter(status='active').count()
        
        type_stats = {}
        for tax_type, _ in TaxRate.TAX_TYPES:
            type_stats[tax_type] = self.get_queryset().filter(tax_type=tax_type).count()
        
        return Response({
            'total_rates': total_rates,
            'active_rates': active_rates,
            'type_stats': type_stats,
        })


class TaxTransactionViewSet(viewsets.ModelViewSet):
    queryset = TaxTransaction.objects.all()
    serializer_class = TaxTransactionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['taxpayer', 'tax_rate', 'transaction_type', 'status']
    search_fields = ['transaction_number', 'description']
    ordering_fields = ['transaction_date', 'amount', 'tax_amount', 'created_at']
    ordering = ['-transaction_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
        
        # فیلتر بر اساس مبلغ
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار تراکنش‌های مالیاتی"""
        total_transactions = self.get_queryset().count()
        total_amount = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        total_tax = self.get_queryset().aggregate(total=Sum('tax_amount'))['total'] or 0
        
        type_stats = {}
        for transaction_type, _ in TaxTransaction.TRANSACTION_TYPES:
            type_stats[transaction_type] = self.get_queryset().filter(transaction_type=transaction_type).count()
        
        status_stats = {}
        for status, _ in TaxTransaction.STATUS_CHOICES:
            status_stats[status] = self.get_queryset().filter(status=status).count()
        
        return Response({
            'total_transactions': total_transactions,
            'total_amount': total_amount,
            'total_tax': total_tax,
            'type_stats': type_stats,
            'status_stats': status_stats,
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """تأیید تراکنش مالیاتی"""
        transaction = self.get_object()
        
        if transaction.status != 'pending':
            return Response({'error': 'فقط تراکنش‌های در انتظار تأیید قابل تأیید هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transaction.status = 'approved'
        transaction.save()
        
        return Response({'message': 'تراکنش مالیاتی با موفقیت تأیید شد'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """رد تراکنش مالیاتی"""
        transaction = self.get_object()
        
        if transaction.status != 'pending':
            return Response({'error': 'فقط تراکنش‌های در انتظار تأیید قابل رد هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transaction.status = 'rejected'
        transaction.save()
        
        return Response({'message': 'تراکنش مالیاتی رد شد'})
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """گزارش مالیاتی"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        if not date_from or not date_to:
            return Response({'error': 'تاریخ شروع و پایان الزامی است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        transactions = self.get_queryset().filter(
            transaction_date__gte=date_from,
            transaction_date__lte=date_to
        )
        
        # آمار کلی
        total_transactions = transactions.count()
        total_amount = transactions.aggregate(total=Sum('amount'))['total'] or 0
        total_tax = transactions.aggregate(total=Sum('tax_amount'))['total'] or 0
        
        # آمار بر اساس نوع تراکنش
        type_stats = {}
        for transaction_type, _ in TaxTransaction.TRANSACTION_TYPES:
            type_transactions = transactions.filter(transaction_type=transaction_type)
            type_stats[transaction_type] = {
                'count': type_transactions.count(),
                'amount': type_transactions.aggregate(total=Sum('amount'))['total'] or 0,
                'tax': type_transactions.aggregate(total=Sum('tax_amount'))['total'] or 0,
            }
        
        # آمار بر اساس مودی
        taxpayer_stats = {}
        for taxpayer in transactions.values('taxpayer__name').distinct():
            taxpayer_name = taxpayer['taxpayer__name']
            taxpayer_transactions = transactions.filter(taxpayer__name=taxpayer_name)
            taxpayer_stats[taxpayer_name] = {
                'count': taxpayer_transactions.count(),
                'amount': taxpayer_transactions.aggregate(total=Sum('amount'))['total'] or 0,
                'tax': taxpayer_transactions.aggregate(total=Sum('tax_amount'))['total'] or 0,
            }
        
        return Response({
            'period': {
                'from': date_from,
                'to': date_to,
            },
            'summary': {
                'total_transactions': total_transactions,
                'total_amount': total_amount,
                'total_tax': total_tax,
            },
            'by_type': type_stats,
            'by_taxpayer': taxpayer_stats,
        })