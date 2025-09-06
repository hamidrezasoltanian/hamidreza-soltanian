from rest_framework import serializers
from .models import Invoice, InvoiceItem, Quotation, QuotationItem, Payment


class InvoiceItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    
    class Meta:
        model = InvoiceItem
        fields = '__all__'
        read_only_fields = ('invoice',)


class InvoiceSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    items = InvoiceItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'approved_by', 'approved_at')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class InvoiceListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست فاکتورها (بدون جزئیات کامل)"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_name', 'contact_person_name',
            'invoice_date', 'due_date', 'total_amount', 'paid_amount', 'remaining_amount',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'created_at', 'created_by'
        ]


class QuotationItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    
    class Meta:
        model = QuotationItem
        fields = '__all__'
        read_only_fields = ('quotation',)


class QuotationSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    items = QuotationItemSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Quotation
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'converted_to_invoice')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class QuotationListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست پیش‌فاکتورها (بدون جزئیات کامل)"""
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = Quotation
        fields = [
            'id', 'quotation_number', 'customer', 'customer_name', 'contact_person_name',
            'quotation_date', 'valid_until', 'total_amount', 'status', 'status_display',
            'is_expired', 'created_at', 'created_by'
        ]


class PaymentSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)