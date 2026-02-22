"""
Service Request Serializers - REST API serializers for service request management
"""
from datetime import timedelta
import os
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.service_requests.models import (
    ServiceCategory, Service, ServiceRequest, ServiceRequestApproval,
    ServiceRequestItem, ServiceRequestAttachment
)
from apps.organizations.models import Organization
from apps.sla.utils import (
    apply_sla_dates,
    apply_sla_pause,
    resolve_sla_targets,
    select_sla_policy_for_service_request,
    _priority_to_severity,
)


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

    def validate_file(self, value):
        if not value:
            raise ValidationError('File is required.')
        max_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 10)
        max_bytes = int(max_mb) * 1024 * 1024
        if value.size > max_bytes:
            raise ValidationError(f'File size exceeds {max_mb} MB limit.')
        return value

    def _populate_file_metadata(self, attrs):
        uploaded = attrs.get('file')
        if not uploaded:
            return
        attrs['filename'] = os.path.basename(uploaded.name)
        attrs['file_size'] = uploaded.size
        attrs['file_type'] = getattr(uploaded, 'content_type', '') or ''

    def create(self, validated_data):
        self._populate_file_metadata(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        self._populate_file_metadata(validated_data)
        return super().update(instance, validated_data)


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
            'sla_response_due_date', 'sla_response_breach',
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
            'submitted_at', 'approved_at', 'fulfilled_at', 'due_date', 'first_response_at',
            'sla_policy', 'sla_response_due_date', 'sla_response_breach',
            'sla_due_date', 'sla_breach', 'sla_paused_at', 'sla_pause_total_minutes',
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

        instance = super().create(validated_data)
        if not instance.sla_policy:
            policy = select_sla_policy_for_service_request(instance)
            if policy:
                instance.sla_policy = policy
                severity = _priority_to_severity(instance.priority, is_incident=False)
                response_minutes, resolution_minutes = resolve_sla_targets(policy, severity)
                updated = ['sla_policy']
                base_time = instance.submitted_at or instance.created_at
                updated.extend(apply_sla_dates(instance, response_minutes, resolution_minutes, base_time))
                instance.save(update_fields=sorted(set(updated)))
        return instance

    def update(self, instance, validated_data):
        service = validated_data.get('service') if 'service' in validated_data else instance.service
        due_date = validated_data.get('due_date') if 'due_date' in validated_data else instance.due_date
        sla_due_date = validated_data.get('sla_due_date') if 'sla_due_date' in validated_data else instance.sla_due_date

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if instance.first_response_at is None and instance.status in {'in_progress', 'approved'}:
            instance.first_response_at = timezone.now()

        if service and not due_date:
            instance.due_date = timezone.now() + timedelta(hours=service.fulfillment_time_hours)
        if service and not sla_due_date:
            instance.sla_due_date = timezone.now() + timedelta(hours=service.fulfillment_time_hours)

        instance.save()
        pause_fields = []
        pause_fields.extend(apply_sla_pause(
            instance,
            instance.status in {'pending_approval', 'pending_fulfillment'}
        ))
        if pause_fields:
            instance.save(update_fields=sorted(set(pause_fields)))
        if not instance.sla_policy:
            policy = select_sla_policy_for_service_request(instance)
            if policy:
                instance.sla_policy = policy
                severity = _priority_to_severity(instance.priority, is_incident=False)
                response_minutes, resolution_minutes = resolve_sla_targets(policy, severity)
                updated = ['sla_policy']
                base_time = instance.submitted_at or instance.created_at
                updated.extend(apply_sla_dates(instance, response_minutes, resolution_minutes, base_time))
                instance.save(update_fields=sorted(set(updated)))
        if instance.update_breach_status():
            instance.save(update_fields=['sla_breach'])
        return instance

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        org = self._resolve_org(attrs, instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        requester = attrs.get('requester') if 'requester' in attrs else getattr(instance, 'requester', None)
        if user and user.role == 'end_user' and requester and requester.id != user.id:
            raise ValidationError({'requester': 'End users can only set themselves as requester.'})

        if user and user.role == 'end_user' and attrs.get('assigned_to') is not None:
            raise ValidationError({'assigned_to': 'End users cannot assign service requests.'})

        for field_name in ['requester', 'assigned_to']:
            value = attrs.get(field_name) if field_name in attrs else getattr(instance, field_name, None)
            self._validate_user_org(value, org, field_name)

        service = attrs.get('service') if 'service' in attrs else getattr(instance, 'service', None)
        self._validate_service_org(service, org, 'service')

        sla_policy = attrs.get('sla_policy') if 'sla_policy' in attrs else getattr(instance, 'sla_policy', None)
        self._validate_policy_org(sla_policy, org, 'sla_policy')

        return attrs

    def _resolve_org(self, attrs, instance=None):
        org = attrs.get('organization') if attrs else None
        if org:
            return org
        if instance and getattr(instance, 'organization', None):
            return instance.organization
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        user_org = getattr(user, 'organization', None) if user else None
        if user_org:
            matched = Organization.objects.filter(name=user_org.name).first()
            if matched:
                return matched
        if user and user.is_superuser:
            return Organization.objects.filter(is_active=True).first()
        return None

    def _validate_user_org(self, user, org, field_name):
        if not user or not org:
            return
        user_org = getattr(user, 'organization', None)
        if not user_org or user_org.name != org.name:
            raise ValidationError({field_name: 'User must belong to the same organization.'})

    def _validate_service_org(self, service, org, field_name):
        if not service or not org:
            return
        if service.organization_id != org.id:
            raise ValidationError({field_name: 'Service must belong to the same organization.'})

    def _validate_policy_org(self, policy, org, field_name):
        if not policy or not org:
            return
        if getattr(policy, 'organization_id', None) != org.id:
            raise ValidationError({field_name: 'SLA policy must belong to the same organization.'})


class ServiceRequestActionSerializer(serializers.Serializer):
    """Serializer for service request actions"""
    action = serializers.ChoiceField(choices=['approve', 'reject', 'submit', 'complete', 'cancel'])
    comments = serializers.CharField(required=False, allow_blank=True)
