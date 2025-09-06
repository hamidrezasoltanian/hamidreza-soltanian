from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum
from django.utils import timezone
from .models import Invoice, InvoiceItem, Quotation, QuotationItem, Payment
from .serializers import (
    InvoiceSerializer, InvoiceListSerializer, InvoiceItemSerializer,
    QuotationSerializer, QuotationListSerializer, QuotationItemSerializer,
    PaymentSerializer
)


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'status', 'payment_status', 'invoice_type']
    search_fields = ['invoice_number', 'customer__first_name', 'customer__last_name', 'customer__company_name']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(invoice_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(invoice_date__lte=date_to)
        
        # فیلتر بر اساس مبلغ
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        
        if min_amount:
            queryset = queryset.filter(total_amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(total_amount__lte=max_amount)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی فاکتورها"""
        total_invoices = self.get_queryset().count()
        total_amount = self.get_queryset().aggregate(total=Sum('total_amount'))['total'] or 0
        paid_amount = self.get_queryset().aggregate(total=Sum('paid_amount'))['total'] or 0
        pending_amount = total_amount - paid_amount
        
        status_stats = {}
        for status, _ in Invoice.STATUS_CHOICES:
            status_stats[status] = self.get_queryset().filter(status=status).count()
        
        return Response({
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'pending_amount': pending_amount,
            'status_stats': status_stats,
        })
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """تأیید فاکتور"""
        invoice = self.get_object()
        
        if invoice.status != 'pending_approval':
            return Response({'error': 'فقط فاکتورهای در انتظار تأیید قابل تأیید هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'approved'
        invoice.approved_by = request.user
        invoice.approved_at = timezone.now()
        invoice.save()
        
        return Response({'message': 'فاکتور با موفقیت تأیید شد'})
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """لغو فاکتور"""
        invoice = self.get_object()
        
        if invoice.status in ['cancelled', 'paid']:
            return Response({'error': 'فاکتور قابل لغو نیست'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'cancelled'
        invoice.save()
        
        return Response({'message': 'فاکتور لغو شد'})
    
    @action(detail=True, methods=['post'])
    def add_payment(self, request, pk=None):
        """اضافه کردن پرداخت"""
        invoice = self.get_object()
        payment_data = request.data.copy()
        payment_data['invoice'] = invoice.id
        
        serializer = PaymentSerializer(data=payment_data, context={'request': request})
        if serializer.is_valid():
            payment = serializer.save()
            
            # بروزرسانی مبلغ پرداخت شده
            invoice.paid_amount += payment.amount
            if invoice.paid_amount >= invoice.total_amount:
                invoice.payment_status = 'paid'
            elif invoice.paid_amount > 0:
                invoice.payment_status = 'partial'
            invoice.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['invoice', 'product']
    ordering_fields = ['sort_order', 'total_amount']
    ordering = ['invoice', 'sort_order']


class QuotationViewSet(viewsets.ModelViewSet):
    queryset = Quotation.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'status']
    search_fields = ['quotation_number', 'customer__first_name', 'customer__last_name', 'customer__company_name']
    ordering_fields = ['quotation_date', 'valid_until', 'total_amount', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuotationListSerializer
        return QuotationSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(quotation_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(quotation_date__lte=date_to)
        
        # فیلتر بر اساس انقضا
        expired = self.request.query_params.get('expired')
        if expired == 'true':
            queryset = queryset.filter(valid_until__lt=timezone.now().date())
        elif expired == 'false':
            queryset = queryset.filter(valid_until__gte=timezone.now().date())
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی پیش‌فاکتورها"""
        total_quotations = self.get_queryset().count()
        total_amount = self.get_quotations().aggregate(total=Sum('total_amount'))['total'] or 0
        expired_quotations = self.get_queryset().filter(valid_until__lt=timezone.now().date()).count()
        
        status_stats = {}
        for status, _ in Quotation.STATUS_CHOICES:
            status_stats[status] = self.get_queryset().filter(status=status).count()
        
        return Response({
            'total_quotations': total_quotations,
            'total_amount': total_amount,
            'expired_quotations': expired_quotations,
            'status_stats': status_stats,
        })
    
    @action(detail=True, methods=['post'])
    def convert_to_invoice(self, request, pk=None):
        """تبدیل پیش‌فاکتور به فاکتور"""
        quotation = self.get_object()
        
        if quotation.status != 'accepted':
            return Response({'error': 'فقط پیش‌فاکتورهای پذیرفته شده قابل تبدیل هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # ایجاد فاکتور جدید
        invoice = Invoice.objects.create(
            invoice_number=f"INV-{quotation.quotation_number}",
            customer=quotation.customer,
            contact_person=quotation.contact_person,
            invoice_date=timezone.now().date(),
            subtotal=quotation.subtotal,
            discount_amount=quotation.discount_amount,
            discount_percentage=quotation.discount_percentage,
            tax_amount=quotation.tax_amount,
            tax_percentage=quotation.tax_percentage,
            total_amount=quotation.total_amount,
            notes=quotation.notes,
            terms_conditions=quotation.terms_conditions,
            created_by=request.user
        )
        
        # کپی کردن آیتم‌ها
        for item in quotation.items.all():
            InvoiceItem.objects.create(
                invoice=invoice,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount_amount=item.discount_amount,
                discount_percentage=item.discount_percentage,
                tax_amount=item.tax_amount,
                total_amount=item.total_amount,
                description=item.description,
                sort_order=item.sort_order
            )
        
        # بروزرسانی وضعیت پیش‌فاکتور
        quotation.status = 'converted'
        quotation.converted_to_invoice = invoice
        quotation.save()
        
        return Response({
            'message': 'پیش‌فاکتور با موفقیت به فاکتور تبدیل شد',
            'invoice_id': invoice.id,
            'invoice_number': invoice.invoice_number
        })


class QuotationItemViewSet(viewsets.ModelViewSet):
    queryset = QuotationItem.objects.all()
    serializer_class = QuotationItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['quotation', 'product']
    ordering_fields = ['sort_order', 'total_amount']
    ordering = ['quotation', 'sort_order']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['invoice', 'payment_method', 'status']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(payment_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(payment_date__lte=date_to)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی پرداخت‌ها"""
        total_payments = self.get_queryset().count()
        total_amount = self.get_queryset().aggregate(total=Sum('amount'))['total'] or 0
        
        method_stats = {}
        for method, _ in Payment.PAYMENT_METHODS:
            method_stats[method] = self.get_queryset().filter(payment_method=method).count()
        
        return Response({
            'total_payments': total_payments,
            'total_amount': total_amount,
            'method_stats': method_stats,
        })