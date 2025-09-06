from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Personnel, PersonnelContact, PersonnelDocument
from .serializers import (
    PersonnelSerializer, PersonnelListSerializer, 
    PersonnelContactSerializer, PersonnelDocumentSerializer
)


class PersonnelViewSet(viewsets.ModelViewSet):
    queryset = Personnel.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer', 'position', 'department', 'is_primary_contact', 'is_authorized_for_orders']
    search_fields = ['first_name', 'last_name', 'mobile_number', 'email', 'national_id']
    ordering_fields = ['first_name', 'last_name', 'position', 'created_at']
    ordering = ['customer', 'last_name', 'first_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PersonnelListSerializer
        return PersonnelSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # فیلتر بر اساس مشتری
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        # فیلتر بر اساس مجوزها
        authorized_for_orders = self.request.query_params.get('authorized_for_orders')
        if authorized_for_orders == 'true':
            queryset = queryset.filter(is_authorized_for_orders=True)
        
        authorized_for_payment = self.request.query_params.get('authorized_for_payment')
        if authorized_for_payment == 'true':
            queryset = queryset.filter(is_authorized_for_payment=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """آمار کلی پرسنل"""
        total_personnel = self.get_queryset().count()
        primary_contacts = self.get_queryset().filter(is_primary_contact=True).count()
        authorized_for_orders = self.get_queryset().filter(is_authorized_for_orders=True).count()
        authorized_for_payment = self.get_queryset().filter(is_authorized_for_payment=True).count()
        
        return Response({
            'total_personnel': total_personnel,
            'primary_contacts': primary_contacts,
            'authorized_for_orders': authorized_for_orders,
            'authorized_for_payment': authorized_for_payment,
        })
    
    @action(detail=True, methods=['post'])
    def add_contact(self, request, pk=None):
        """اضافه کردن اطلاعات تماس"""
        personnel = self.get_object()
        contact_data = request.data.copy()
        contact_data['personnel'] = personnel.id
        
        serializer = PersonnelContactSerializer(data=contact_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """اضافه کردن سند"""
        personnel = self.get_object()
        document_data = request.data.copy()
        document_data['personnel'] = personnel.id
        
        serializer = PersonnelDocumentSerializer(data=document_data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonnelContactViewSet(viewsets.ModelViewSet):
    queryset = PersonnelContact.objects.all()
    serializer_class = PersonnelContactSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['personnel', 'contact_type', 'is_primary']
    search_fields = ['value', 'notes']
    ordering_fields = ['contact_type', 'is_primary']
    ordering = ['personnel', 'contact_type']


class PersonnelDocumentViewSet(viewsets.ModelViewSet):
    queryset = PersonnelDocument.objects.all()
    serializer_class = PersonnelDocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['personnel', 'document_type']
    search_fields = ['title', 'description']
    ordering_fields = ['upload_date', 'title']
    ordering = ['-upload_date']
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)