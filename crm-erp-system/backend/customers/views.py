from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Customer, CustomerCategory, CustomerCategoryMembership
from .serializers import CustomerSerializer, CustomerCategorySerializer, CustomerCategoryMembershipSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'status', 'city', 'state']
    search_fields = ['first_name', 'last_name', 'company_name', 'phone_number', 'email', 'customer_code']
    ordering_fields = ['created_at', 'updated_at', 'customer_code', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس تگ‌ها
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            for tag in tag_list:
                queryset = queryset.filter(tags__icontains=tag)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی مشتریان"""
        total_customers = self.get_queryset().count()
        active_customers = self.get_queryset().filter(status='active').count()
        individual_customers = self.get_queryset().filter(customer_type='individual').count()
        legal_customers = self.get_queryset().filter(customer_type='legal').count()
        
        return Response({
            'total_customers': total_customers,
            'active_customers': active_customers,
            'individual_customers': individual_customers,
            'legal_customers': legal_customers,
        })
    
    @action(detail=True, methods=['post'])
    def add_tags(self, request, pk=None):
        """اضافه کردن تگ به مشتری"""
        customer = self.get_object()
        tags = request.data.get('tags', [])
        
        if not isinstance(tags, list):
            return Response({'error': 'تگ‌ها باید به صورت لیست ارسال شوند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        current_tags = customer.get_tags_list()
        new_tags = list(set(current_tags + tags))
        customer.set_tags(new_tags)
        customer.save()
        
        return Response({'message': 'تگ‌ها با موفقیت اضافه شدند'})
    
    @action(detail=True, methods=['post'])
    def remove_tags(self, request, pk=None):
        """حذف تگ از مشتری"""
        customer = self.get_object()
        tags = request.data.get('tags', [])
        
        if not isinstance(tags, list):
            return Response({'error': 'تگ‌ها باید به صورت لیست ارسال شوند'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        current_tags = customer.get_tags_list()
        new_tags = [tag for tag in current_tags if tag not in tags]
        customer.set_tags(new_tags)
        customer.save()
        
        return Response({'message': 'تگ‌ها با موفقیت حذف شدند'})


class CustomerCategoryViewSet(viewsets.ModelViewSet):
    queryset = CustomerCategory.objects.all()
    serializer_class = CustomerCategorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class CustomerCategoryMembershipViewSet(viewsets.ModelViewSet):
    queryset = CustomerCategoryMembership.objects.all()
    serializer_class = CustomerCategoryMembershipSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'category']
    search_fields = ['customer__first_name', 'customer__last_name', 'customer__company_name', 'category__name']
    ordering_fields = ['assigned_at']
    ordering = ['-assigned_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس مشتری
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        return queryset