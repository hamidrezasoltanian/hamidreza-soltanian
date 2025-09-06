from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F
from .models import Product, ProductCategory, ProductImage, ProductAttribute, ProductAttributeValue
from .serializers import (
    ProductSerializer, ProductListSerializer, ProductCategorySerializer, 
    ProductImageSerializer, ProductAttributeSerializer, ProductAttributeValueSerializer
)


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """درخت دسته‌بندی محصولات"""
        categories = ProductCategory.objects.filter(is_active=True).order_by('sort_order', 'name')
        return Response(self.serializer_class(categories, many=True).data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_service', 'is_digital']
    search_fields = ['name', 'name_en', 'product_code', 'barcode', 'description']
    ordering_fields = ['name', 'sale_price', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تگ‌ها
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        
        # فیلتر بر اساس قیمت
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(sale_price__gte=min_price)
        if max_price:
            queryset = queryset.filter(sale_price__lte=max_price)
        
        # فیلتر بر اساس موجودی
        low_stock = self.request.query_params.get('low_stock')
        if low_stock == 'true':
            queryset = queryset.filter(current_stock__lte=F('min_stock'))
        
        out_of_stock = self.request.query_params.get('out_of_stock')
        if out_of_stock == 'true':
            queryset = queryset.filter(current_stock__lte=0)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی محصولات"""
        total_products = self.get_queryset().count()
        active_products = self.get_queryset().filter(status='active').count()
        low_stock_products = self.get_queryset().filter(
            current_stock__lte=F('min_stock')
        ).count()
        out_of_stock_products = self.get_queryset().filter(current_stock__lte=0).count()
        
        return Response({
            'total_products': total_products,
            'active_products': active_products,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
        })
    
    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        """اضافه کردن تگ به محصول"""
        product = self.get_object()
        tags = request.data.get('tags', [])
        
        if not isinstance(tags, list):
            return Response({'error': 'تگ‌ها باید به صورت لیست ارسال شوند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        current_tags = product.get_tags_list()
        new_tags = list(set(current_tags + tags))
        product.set_tags(new_tags)
        product.save()
        
        return Response({'message': 'تگ‌ها با موفقیت اضافه شدند'})
    
    @action(detail=True, methods=['post'])
    def remove_tags(self, request, pk=None):
        """حذف تگ از محصول"""
        product = self.get_object()
        tags = request.data.get('tags', [])
        
        if not isinstance(tags, list):
            return Response({'error': 'تگ‌ها باید به صورت لیست ارسال شوند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        current_tags = product.get_tags_list()
        new_tags = [tag for tag in current_tags if tag not in tags]
        product.set_tags(new_tags)
        product.save()
        
        return Response({'message': 'تگ‌ها با موفقیت حذف شدند'})
    
    @action(detail=True, methods=['post'])
    def update_stock(self, request, pk=None):
        """بروزرسانی موجودی محصول"""
        product = self.get_object()
        quantity = request.data.get('quantity')
        movement_type = request.data.get('movement_type', 'adjustment')
        
        if quantity is None:
            return Response({'error': 'مقدار موجودی الزامی است'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = float(quantity)
            if movement_type == 'in':
                product.current_stock += quantity
            elif movement_type == 'out':
                product.current_stock -= quantity
            else:  # adjustment
                product.current_stock = quantity
            
            if product.current_stock < 0:
                return Response({'error': 'موجودی نمی‌تواند منفی باشد'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            product.save()
            return Response({'message': 'موجودی با موفقیت بروزرسانی شد'})
        
        except ValueError:
            return Response({'error': 'مقدار موجودی باید عدد باشد'}, 
                          status=status.HTTP_400_BAD_REQUEST)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'is_primary']
    ordering_fields = ['sort_order', 'created_at']
    ordering = ['product', 'sort_order']


class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['attribute_type', 'is_required', 'is_filterable', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['sort_order', 'name']
    ordering = ['sort_order', 'name']


class ProductAttributeValueViewSet(viewsets.ModelViewSet):
    queryset = ProductAttributeValue.objects.all()
    serializer_class = ProductAttributeValueSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'attribute']
    ordering_fields = ['product', 'attribute']
    ordering = ['product', 'attribute']