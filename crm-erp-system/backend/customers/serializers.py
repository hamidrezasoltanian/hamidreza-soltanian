from rest_framework import serializers
from .models import Customer, CustomerCategory, CustomerCategoryMembership


class CustomerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategory
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by')
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CustomerCategoryMembershipSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = CustomerCategoryMembership
        fields = '__all__'
        read_only_fields = ('assigned_at', 'assigned_by')
    
    def create(self, validated_data):
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)