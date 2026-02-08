"""
Service Request Serializers - REST API serializers for service request management
"""
from rest_framework import serializers
from apps.service_requests.models import (
    ServiceCategory, Service, ServiceRequest, ServiceRequestApproval,
    ServiceRequestItem, ServiceRequestAttachment
)


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories"""
    service_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ServiceCategory
        fields = ['id', 'organization', 'name', 'description', 'icon', 'color', 'service_count', 'is_active']
    
    def get_service_count(self, obj):
        return obj.service_set.count()


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight service serializer for lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'category_name', 'description', 'is_active']


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Full service detail serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'organization', 'name', 'description', 'category', 'category_name',
            'owner', 'owner_name', 'manager', 'manager_name', 'sla_policy',
            'cost_model', 'support_hours', 'availability_target', 'is_active',
            'created_at', 'updated_at'
        ]


class ServiceRequestItemSerializer(serializers.ModelSerializer):
    """Serializer for items in a service request"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    
    class Meta:
        model = ServiceRequestItem
        fields = [
            'id', 'service_request', 'service', 'service_name', 'quantity',
            'unit_cost', 'total_cost', 'status', 'created_at'
        ]


class ServiceRequestApprovalSerializer(serializers.ModelSerializer):
    """Serializer for service request approvals"""
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)
    
    class Meta:
        model = ServiceRequestApproval
        fields = [
            'id', 'service_request', 'approver', 'approver_name', 'status',
            'comments', 'approved_at', 'approval_order'
        ]


class ServiceRequestAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for service request attachments"""
    class Meta:
        model = ServiceRequestAttachment
        fields = ['id', 'service_request', 'file', 'filename', 'file_type', 'created_at']


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Lightweight service request list serializer"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'request_number', 'title', 'requester', 'requester_name',
            'status', 'status_display', 'total_cost', 'sla_due_date', 'created_at'
        ]


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Full service request detail serializer with nested relations"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Nested serializers
    items = ServiceRequestItemSerializer(many=True, read_only=True, source='servicerequestitem_set')
    approvals = ServiceRequestApprovalSerializer(many=True, read_only=True, source='approval_set')
    attachments = ServiceRequestAttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'organization', 'request_number', 'title', 'description',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name',
            'status', 'status_display', 'priority', 'priority_display',
            'category', 'estimated_cost', 'actual_cost', 'total_cost',
            'start_date', 'target_completion_date', 'actual_completion_date',
            'sla_policy', 'sla_due_date', 'sla_breach',
            'approval_required', 'approval_level',
            'items', 'approvals', 'attachments',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['request_number', 'created_at', 'updated_at']


class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service requests"""
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'category', 'requester', 'assigned_to',
            'priority', 'start_date', 'target_completion_date'
        ]
    
    def create(self, validated_data):
        # Generate request number
        org = validated_data.get('organization')
        count = ServiceRequest.objects.filter(organization=org).count()
        validated_data['request_number'] = f"{org.slug.upper()}-SR-{count + 1:05d}"
        
        return super().create(validated_data)


class ServiceRequestActionSerializer(serializers.Serializer):
    """Serializer for service request actions"""
    action = serializers.ChoiceField(choices=['approve', 'reject', 'submit', 'complete', 'cancel'])
    comments = serializers.CharField(required=False, allow_blank=True)
