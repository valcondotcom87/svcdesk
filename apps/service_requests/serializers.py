"""
Service Request Serializers - REST API serializers for service request management
"""
from datetime import timedelta
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.service_requests.models import (
    ServiceCategory, Service, ServiceRequest, ServiceRequestApproval,
    ServiceRequestItem, ServiceRequestAttachment
)
from apps.organizations.models import Organization


class ServiceCategorySerializer(serializers.ModelSerializer):
    """Serializer for service categories"""
    service_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'organization', 'name', 'description', 'icon', 'service_count', 'is_active']
        extra_kwargs = {
            'organization': {'required': False, 'allow_null': True},
        }

    def get_service_count(self, obj):
        return obj.services.count()


class ServiceListSerializer(serializers.ModelSerializer):
    """Lightweight service serializer for lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'category', 'category_name', 'description', 'is_active']


class ServiceDetailSerializer(serializers.ModelSerializer):
    """Full service detail serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'organization', 'name', 'description', 'category', 'category_name',
            'short_description', 'icon', 'fulfillment_time_hours', 'requires_approval',
            'approval_group', 'is_active', 'created_at', 'updated_at'
        ]


class ServiceCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating services"""
    class Meta:
        model = Service
        fields = [
            'name', 'description', 'category', 'short_description', 'icon',
            'fulfillment_time_hours', 'requires_approval', 'approval_group',
            'is_active'
        ]


class ServiceRequestItemSerializer(serializers.ModelSerializer):
    """Serializer for items in a service request"""
    class Meta:
        model = ServiceRequestItem
        fields = ['id', 'request', 'item_type', 'quantity', 'description', 'created_at']


class ServiceRequestApprovalSerializer(serializers.ModelSerializer):
    """Serializer for service request approvals"""
    approver_name = serializers.CharField(source='approver.get_full_name', read_only=True)

    class Meta:
        model = ServiceRequestApproval
        fields = [
            'id', 'request', 'approval_level', 'approver', 'approver_name',
            'approval_group', 'status', 'notes', 'decided_at', 'created_at'
        ]


class ServiceRequestAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for service request attachments"""
    class Meta:
        model = ServiceRequestAttachment
        fields = ['id', 'request', 'file', 'filename', 'file_type', 'file_size', 'created_at']


class ServiceRequestListSerializer(serializers.ModelSerializer):
    """Lightweight service request list serializer"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_category_name = serializers.CharField(source='service.category.name', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'ticket_number', 'title', 'service', 'service_name', 'service_category_name',
            'requester', 'requester_name',
            'status', 'status_display', 'priority', 'priority_display',
            'sla_due_date', 'sla_breach', 'due_date', 'created_at'
        ]


class ServiceRequestDetailSerializer(serializers.ModelSerializer):
    """Full service request detail serializer with nested relations"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    service_category_name = serializers.CharField(source='service.category.name', read_only=True)

    items = ServiceRequestItemSerializer(many=True, read_only=True)
    approvals = ServiceRequestApprovalSerializer(many=True, read_only=True)
    attachments = ServiceRequestAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceRequest
        fields = [
            'id', 'organization', 'ticket_number', 'service', 'service_name', 'service_category_name',
            'title', 'description',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name',
            'status', 'status_display', 'priority', 'priority_display',
            'submitted_at', 'approved_at', 'fulfilled_at', 'due_date',
            'sla_policy', 'sla_due_date', 'sla_breach',
            'items', 'approvals', 'attachments',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['ticket_number', 'created_at', 'updated_at']


class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating service requests"""
    class Meta:
        model = ServiceRequest
        fields = [
            'title', 'description', 'service', 'requester', 'assigned_to',
            'priority', 'due_date', 'sla_policy'
        ]
        extra_kwargs = {
            'service': {'required': False, 'allow_null': True},
            'requester': {'required': False, 'allow_null': True},
            'assigned_to': {'required': False, 'allow_null': True},
            'priority': {'required': False},
            'due_date': {'required': False, 'allow_null': True},
            'sla_policy': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        org = validated_data.get('organization')
        if not org:
            request = self.context.get('request')
            user = getattr(request, 'user', None)
            user_org = getattr(user, 'organization', None) if user else None
            if user_org:
                org = Organization.objects.filter(name=user_org.name).first()
            if not org and user and user.is_superuser:
                org = Organization.objects.filter(is_active=True).first()
            if not org:
                raise ValidationError({'organization': 'Organization is required to create a service request.'})
            validated_data['organization'] = org
        count = ServiceRequest.objects.filter(organization=org).count()
        validated_data['ticket_number'] = f"{org.slug.upper()}-SR-{count + 1:05d}"

        service = validated_data.get('service')
        if service and not validated_data.get('due_date'):
            due = timezone.now() + timedelta(hours=service.fulfillment_time_hours)
            validated_data['due_date'] = due
        if service and not validated_data.get('sla_due_date'):
            sla_due = timezone.now() + timedelta(hours=service.fulfillment_time_hours)
            validated_data['sla_due_date'] = sla_due

        return super().create(validated_data)

    def update(self, instance, validated_data):
        service = validated_data.get('service') if 'service' in validated_data else instance.service
        due_date = validated_data.get('due_date') if 'due_date' in validated_data else instance.due_date
        sla_due_date = validated_data.get('sla_due_date') if 'sla_due_date' in validated_data else instance.sla_due_date

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if service and not due_date:
            instance.due_date = timezone.now() + timedelta(hours=service.fulfillment_time_hours)
        if service and not sla_due_date:
            instance.sla_due_date = timezone.now() + timedelta(hours=service.fulfillment_time_hours)

        instance.save()
        if instance.update_breach_status():
            instance.save(update_fields=['sla_breach'])
        return instance


class ServiceRequestActionSerializer(serializers.Serializer):
    """Serializer for service request actions"""
    action = serializers.ChoiceField(choices=['approve', 'reject', 'submit', 'complete', 'cancel'])
    comments = serializers.CharField(required=False, allow_blank=True)
