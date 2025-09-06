from rest_framework import serializers
from .models import Personnel, PersonnelContact, PersonnelDocument


class PersonnelContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelContact
        fields = '__all__'
        read_only_fields = ('personnel',)


class PersonnelDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonnelDocument
        fields = '__all__'
        read_only_fields = ('personnel', 'upload_date', 'uploaded_by')
    
    def create(self, validated_data):
        validated_data['uploaded_by'] = self.context['request'].user
        return super().create(validated_data)


class PersonnelSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    contacts = PersonnelContactSerializer(many=True, read_only=True)
    documents = PersonnelDocumentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    
    class Meta:
        model = Personnel
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class PersonnelListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست پرسنل (بدون جزئیات کامل)"""
    full_name = serializers.ReadOnlyField()
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    customer_company = serializers.CharField(source='customer.company_name', read_only=True)
    
    class Meta:
        model = Personnel
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'position',
            'customer', 'customer_name', 'customer_company', 'mobile_number',
            'email', 'is_primary_contact', 'created_at'
        ]