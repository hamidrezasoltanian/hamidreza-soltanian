from rest_framework import serializers
from .models import TaxPayer, TaxRate, TaxTransaction


class TaxPayerSerializer(serializers.ModelSerializer):
    taxpayer_type_display = serializers.CharField(source='get_taxpayer_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TaxPayer
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaxRateSerializer(serializers.ModelSerializer):
    tax_type_display = serializers.CharField(source='get_tax_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TaxRate
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaxTransactionSerializer(serializers.ModelSerializer):
    transaction_type_display = serializers.CharField(source='get_transaction_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    taxpayer_name = serializers.CharField(source='taxpayer.name', read_only=True)
    tax_rate_display = serializers.CharField(source='tax_rate.tax_type', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = TaxTransaction
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)