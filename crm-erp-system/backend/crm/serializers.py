from rest_framework import serializers
from .models import SalesProcess, ProcessStage, ProcessActivity, Lead, Task


class ProcessStageSerializer(serializers.ModelSerializer):
    completed_by_name = serializers.CharField(source='completed_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProcessStage
        fields = '__all__'
        read_only_fields = ('process', 'completed_at', 'completed_by')
    
    def create(self, validated_data):
        validated_data['completed_by'] = self.context['request'].user
        return super().create(validated_data)


class ProcessActivitySerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProcessActivity
        fields = '__all__'
        read_only_fields = ('process', 'created_by')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SalesProcessSerializer(serializers.ModelSerializer):
    weighted_value = serializers.ReadOnlyField()
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    process_type_display = serializers.CharField(source='get_process_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    stages = ProcessStageSerializer(many=True, read_only=True)
    activities = ProcessActivitySerializer(many=True, read_only=True)
    
    class Meta:
        model = SalesProcess
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'assigned_to')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SalesProcessListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست فرایندهای فروش (بدون جزئیات کامل)"""
    weighted_value = serializers.ReadOnlyField()
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    contact_person_name = serializers.CharField(source='contact_person.full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    process_type_display = serializers.CharField(source='get_process_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = SalesProcess
        fields = [
            'id', 'process_name', 'process_type', 'process_type_display', 'priority', 'priority_display',
            'customer', 'customer_name', 'contact_person_name', 'assigned_to_name',
            'estimated_value', 'actual_value', 'probability', 'weighted_value',
            'start_date', 'expected_close_date', 'actual_close_date', 'created_at'
        ]


class LeadSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    converted_customer_name = serializers.CharField(source='converted_to_customer.full_name', read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'converted_at', 'created_by', 'assigned_to', 'converted_to_customer')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class LeadListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست سرنخ‌ها (بدون جزئیات کامل)"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    source_display = serializers.CharField(source='get_source_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Lead
        fields = [
            'id', 'lead_name', 'company_name', 'contact_person', 'email', 'phone',
            'source', 'source_display', 'status', 'status_display', 'industry',
            'company_size', 'estimated_value', 'assigned_to_name', 'created_at'
        ]


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'assigned_to', 'completed_at')
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Serializer برای لیست وظایف (بدون جزئیات کامل)"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'priority', 'priority_display', 'status', 'status_display',
            'assigned_to_name', 'due_date', 'completed_at', 'created_at'
        ]