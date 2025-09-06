from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Sum
from django.utils import timezone
from .models import (
    Warehouse, InventoryItem, LotNumber, StockMovement, 
    StockAdjustment, StockAdjustmentItem
)
from .serializers import (
    WarehouseSerializer, InventoryItemSerializer, LotNumberSerializer,
    StockMovementSerializer, StockAdjustmentSerializer, StockAdjustmentItemSerializer
)


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'address', 'manager']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']


class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'product']
    search_fields = ['product__name', 'product__product_code', 'location']
    ordering_fields = ['product__name', 'quantity', 'last_updated']
    ordering = ['warehouse', 'product__name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس انبار
        warehouse_id = self.request.query_params.get('warehouse_id')
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
        
        # فیلتر بر اساس موجودی کم
        low_stock = self.request.query_params.get('low_stock')
        if low_stock == 'true':
            queryset = queryset.filter(quantity__lte=F('min_quantity'))
        
        # فیلتر بر اساس موجودی تمام شده
        out_of_stock = self.request.query_params.get('out_of_stock')
        if out_of_stock == 'true':
            queryset = queryset.filter(quantity__lte=0)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی موجودی"""
        total_items = self.get_queryset().count()
        low_stock_items = self.get_queryset().filter(quantity__lte=F('min_quantity')).count()
        out_of_stock_items = self.get_queryset().filter(quantity__lte=0).count()
        total_value = self.get_queryset().aggregate(
            total=Sum(F('quantity') * F('product__cost_price'))
        )['total'] or 0
        
        return Response({
            'total_items': total_items,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_value': total_value,
        })
    
    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """تعدیل موجودی"""
        item = self.get_object()
        quantity = request.data.get('quantity')
        movement_type = request.data.get('movement_type', 'adjustment')
        notes = request.data.get('notes', '')
        
        if quantity is None:
            return Response({'error': 'مقدار موجودی الزامی است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = float(quantity)
            old_quantity = item.quantity
            
            if movement_type == 'in':
                item.quantity += quantity
            elif movement_type == 'out':
                item.quantity -= quantity
            else:  # adjustment
                item.quantity = quantity
            
            if item.quantity < 0:
                return Response({'error': 'موجودی نمی‌تواند منفی باشد'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            item.save()
            
            # ثبت حرکت موجودی
            StockMovement.objects.create(
                movement_type=movement_type,
                product=item.product,
                warehouse=item.warehouse,
                quantity=abs(quantity),
                unit_cost=item.product.cost_price,
                total_cost=abs(quantity) * item.product.cost_price,
                notes=notes,
                created_by=request.user
            )
            
            return Response({
                'message': 'موجودی با موفقیت بروزرسانی شد',
                'old_quantity': old_quantity,
                'new_quantity': item.quantity,
                'difference': item.quantity - old_quantity
            })
        
        except ValueError:
            return Response({'error': 'مقدار موجودی باید عدد باشد'}, 
                          status=status.HTTP_400_BAD_REQUEST)


class LotNumberViewSet(viewsets.ModelViewSet):
    queryset = LotNumber.objects.all()
    serializer_class = LotNumberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse', 'supplier']
    search_fields = ['lot_number', 'batch_number', 'supplier']
    ordering_fields = ['lot_number', 'production_date', 'expiry_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس انقضا
        expired = self.request.query_params.get('expired')
        if expired == 'true':
            queryset = queryset.filter(expiry_date__lt=timezone.now().date())
        elif expired == 'false':
            queryset = queryset.filter(expiry_date__gte=timezone.now().date())
        
        # فیلتر بر اساس انقضای نزدیک
        expiring_soon = self.request.query_params.get('expiring_soon')
        if expiring_soon:
            try:
                days = int(expiring_soon)
                future_date = timezone.now().date() + timezone.timedelta(days=days)
                queryset = queryset.filter(expiry_date__lte=future_date)
            except ValueError:
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار شماره لات‌ها"""
        total_lots = self.get_queryset().count()
        expired_lots = self.get_queryset().filter(expiry_date__lt=timezone.now().date()).count()
        expiring_soon = self.get_queryset().filter(
            expiry_date__lte=timezone.now().date() + timezone.timedelta(days=30)
        ).count()
        
        return Response({
            'total_lots': total_lots,
            'expired_lots': expired_lots,
            'expiring_soon': expiring_soon,
        })


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['movement_type', 'product', 'warehouse', 'destination_warehouse']
    search_fields = ['description', 'notes']
    ordering_fields = ['movement_date', 'quantity', 'total_cost']
    ordering = ['-movement_date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تاریخ
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(movement_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(movement_date__lte=date_to)
        
        return queryset


class StockAdjustmentViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['warehouse', 'adjustment_type', 'status']
    search_fields = ['reference_number', 'notes']
    ordering_fields = ['adjustment_date', 'created_at']
    ordering = ['-adjustment_date']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """تأیید تعدیل موجودی"""
        adjustment = self.get_object()
        
        if adjustment.status != 'pending':
            return Response({'error': 'فقط تعدیل‌های در انتظار تأیید قابل تأیید هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        adjustment.status = 'approved'
        adjustment.approved_by = request.user
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        # اعمال تعدیل‌ها
        for item in adjustment.items.all():
            inventory_item = InventoryItem.objects.get(
                product=item.product,
                warehouse=adjustment.warehouse
            )
            inventory_item.quantity = item.actual_quantity
            inventory_item.save()
            
            # ثبت حرکت موجودی
            StockMovement.objects.create(
                movement_type='adjustment',
                product=item.product,
                warehouse=adjustment.warehouse,
                lot_number=item.lot_number,
                quantity=item.difference,
                unit_cost=item.unit_cost,
                total_cost=abs(item.difference) * item.unit_cost,
                reference_type='StockAdjustment',
                reference_id=adjustment.id,
                notes=f'تعدیل موجودی - {adjustment.reference_number}',
                created_by=request.user
            )
        
        return Response({'message': 'تعدیل موجودی با موفقیت تأیید شد'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """رد تعدیل موجودی"""
        adjustment = self.get_object()
        
        if adjustment.status != 'pending':
            return Response({'error': 'فقط تعدیل‌های در انتظار تأیید قابل رد هستند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        adjustment.status = 'rejected'
        adjustment.save()
        
        return Response({'message': 'تعدیل موجودی رد شد'})


class StockAdjustmentItemViewSet(viewsets.ModelViewSet):
    queryset = StockAdjustmentItem.objects.all()
    serializer_class = StockAdjustmentItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['adjustment', 'product', 'lot_number']
    ordering_fields = ['product__name']
    ordering = ['adjustment', 'product__name']