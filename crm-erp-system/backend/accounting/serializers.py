from rest_framework import serializers
from .models import (
    FiscalYear, ChartOfAccounts, Journal, JournalEntry, 
    Ledger, TrialBalance, CostCenter, BankAccount
)


class FiscalYearSerializer(serializers.ModelSerializer):
    is_active = serializers.ReadOnlyField()
    
    class Meta:
        model = FiscalYear
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ChartOfAccountsSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    parent_account_name = serializers.CharField(source='parent_account.account_name', read_only=True)
    level = serializers.ReadOnlyField()
    has_children = serializers.ReadOnlyField()
    
    class Meta:
        model = ChartOfAccounts
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class JournalSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    entries_count = serializers.SerializerMethodField()
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()
    
    class Meta:
        model = Journal
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by', 'approved_by', 'approved_at')
    
    def get_entries_count(self, obj):
        return obj.entries.count()
    
    def get_total_debit(self, obj):
        return obj.entries.aggregate(total=models.Sum('debit_amount'))['total'] or 0
    
    def get_total_credit(self, obj):
        return obj.entries.aggregate(total=models.Sum('credit_amount'))['total'] or 0
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class JournalEntrySerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = JournalEntry
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LedgerSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    balance = serializers.ReadOnlyField()
    
    class Meta:
        model = Ledger
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TrialBalanceSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_code = serializers.CharField(source='account.account_code', read_only=True)
    account_type = serializers.CharField(source='account.account_type', read_only=True)
    
    class Meta:
        model = TrialBalance
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CostCenterSerializer(serializers.ModelSerializer):
    parent_center_name = serializers.CharField(source='parent_center.name', read_only=True)
    level = serializers.ReadOnlyField()
    has_children = serializers.ReadOnlyField()
    
    class Meta:
        model = CostCenter
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class BankAccountSerializer(serializers.ModelSerializer):
    account_type_display = serializers.CharField(source='get_account_type_display', read_only=True)
    currency_display = serializers.CharField(source='get_currency_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = BankAccount
        fields = '__all__'
        read_only_fields = ('created_at', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)