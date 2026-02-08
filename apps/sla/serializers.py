"""
SLA (Service Level Agreement) Serializers
"""
from rest_framework import serializers
from apps.sla.models import (
    SLAPolicy, SLATarget, SLABreach, SLAEscalation, SLAMetric
)


class SLATargetSerializer(serializers.ModelSerializer):
    """Serializer for SLA targets"""
    response_time_hours = serializers.SerializerMethodField()
    resolution_time_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = SLATarget
        fields = [
            'id', 'sla_policy', 'severity', 'response_time_minutes', 'response_time_hours',
            'resolution_time_minutes', 'resolution_time_hours'
        ]
    
    def get_response_time_hours(self, obj):
        return obj.response_time_minutes / 60 if obj.response_time_minutes else None
    
    def get_resolution_time_hours(self, obj):
        return obj.resolution_time_minutes / 60 if obj.resolution_time_minutes else None


class SLAEscalationSerializer(serializers.ModelSerializer):
    """Serializer for SLA escalation rules"""
    escalate_to_name = serializers.CharField(source='escalate_to.get_full_name', read_only=True)
    
    class Meta:
        model = SLAEscalation
        fields = [
            'id', 'sla_policy', 'escalation_level', 'escalation_condition',
            'escalate_to', 'escalate_to_name', 'notification_message'
        ]


class SLABreachSerializer(serializers.ModelSerializer):
    """Serializer for SLA breaches"""
    ticket_number = serializers.CharField(source='incident.ticket_number', read_only=True)
    
    class Meta:
        model = SLABreach
        fields = [
            'id', 'incident', 'ticket_number', 'sla_policy', 'breach_type',
            'breach_reason', 'breached_at', 'reported_to', 'mitigation_actions'
        ]


class SLAMetricSerializer(serializers.ModelSerializer):
    """Serializer for SLA metrics"""
    class Meta:
        model = SLAMetric
        fields = [
            'id', 'sla_policy', 'metric_name', 'metric_value', 'metric_unit',
            'target_value', 'current_value', 'last_updated', 'trend'
        ]


class SLAPolicyListSerializer(serializers.ModelSerializer):
    """Lightweight SLA policy list serializer"""
    target_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SLAPolicy
        fields = [
            'id', 'name', 'description', 'service', 'coverage_type',
            'target_count', 'is_active'
        ]
    
    def get_target_count(self, obj):
        return obj.slatarget_set.count()


class SLAPolicyDetailSerializer(serializers.ModelSerializer):
    """Full SLA policy detail serializer with nested relations"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    coverage_display = serializers.CharField(source='get_coverage_type_display', read_only=True)
    
    # Nested serializers
    targets = SLATargetSerializer(many=True, read_only=True, source='slatarget_set')
    escalations = SLAEscalationSerializer(many=True, read_only=True, source='slaescalation_set')
    metrics = SLAMetricSerializer(many=True, read_only=True, source='slametric_set')
    
    class Meta:
        model = SLAPolicy
        fields = [
            'id', 'organization', 'name', 'description', 'service', 'service_name',
            'coverage_type', 'coverage_display', 'applicable_hours', 'holiday_handling',
            'availability_target', 'targets', 'escalations', 'metrics',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SLAPolicyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating SLA policies"""
    class Meta:
        model = SLAPolicy
        fields = [
            'name', 'description', 'service', 'coverage_type',
            'applicable_hours', 'holiday_handling', 'availability_target'
        ]
