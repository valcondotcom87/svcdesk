"""
SLA (Service Level Agreement) Serializers
"""
from rest_framework import serializers
from apps.sla.models import SLAPolicy, SLATarget, SLABreach, SLAEscalation, SLAMetric


class SLATargetSerializer(serializers.ModelSerializer):
    """Serializer for SLA targets"""
    response_time_hours = serializers.SerializerMethodField()
    resolution_time_hours = serializers.SerializerMethodField()

    class Meta:
        model = SLATarget
        fields = [
            'id', 'sla_policy', 'severity',
            'response_time_minutes', 'response_time_hours',
            'resolution_time_minutes', 'resolution_time_hours'
        ]

    def get_response_time_hours(self, obj):
        return obj.response_time_minutes / 60 if obj.response_time_minutes else None

    def get_resolution_time_hours(self, obj):
        return obj.resolution_time_minutes / 60 if obj.resolution_time_minutes else None


class SLAEscalationSerializer(serializers.ModelSerializer):
    """Serializer for SLA escalation rules"""
    escalate_to_user_name = serializers.CharField(source='escalate_to_user.get_full_name', read_only=True)
    escalate_to_team_name = serializers.CharField(source='escalate_to_team.name', read_only=True)

    class Meta:
        model = SLAEscalation
        fields = [
            'id', 'sla_policy', 'level', 'escalate_after_minutes',
            'escalate_to_team', 'escalate_to_team_name',
            'escalate_to_user', 'escalate_to_user_name',
            'notify_managers', 'action_description'
        ]


class SLABreachSerializer(serializers.ModelSerializer):
    """Serializer for SLA breaches"""
    ticket_number = serializers.CharField(source='incident.ticket_number', read_only=True)

    class Meta:
        model = SLABreach
        fields = [
            'id', 'organization', 'incident', 'service_request', 'ticket_number',
            'sla_policy', 'breach_type', 'target_time', 'breached_at',
            'breach_duration_minutes', 'is_acknowledged', 'created_at', 'updated_at'
        ]


class SLAMetricSerializer(serializers.ModelSerializer):
    """Serializer for SLA metrics"""
    class Meta:
        model = SLAMetric
        fields = [
            'id', 'organization', 'year', 'month',
            'total_incidents', 'breached_incidents', 'compliance_percentage',
            'target_compliance', 'is_compliant'
        ]


class SLAPolicyListSerializer(serializers.ModelSerializer):
    """Lightweight SLA policy list serializer"""
    target_count = serializers.SerializerMethodField()

    class Meta:
        model = SLAPolicy
        fields = [
            'id', 'name', 'description', 'service', 'coverage',
            'response_time', 'resolution_time', 'target_count', 'is_active'
        ]

    def get_target_count(self, obj):
        return obj.targets.count()


class SLAPolicyDetailSerializer(serializers.ModelSerializer):
    """Full SLA policy detail serializer with nested relations"""
    service_name = serializers.CharField(source='service.name', read_only=True)
    coverage_display = serializers.CharField(source='get_coverage_display', read_only=True)
    
    targets = SLATargetSerializer(many=True, read_only=True, source='targets')
    escalations = SLAEscalationSerializer(many=True, read_only=True, source='slaescalation_set')
    metrics = SLAMetricSerializer(many=True, read_only=True, source='slametric_set')
    
    class Meta:
        model = SLAPolicy
        fields = [
            'id', 'organization', 'name', 'description', 'service', 'service_name',
            'incident_category', 'applies_to_priority', 'response_time',
            'resolution_time', 'coverage', 'coverage_display',
            'targets', 'escalations', 'metrics',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class SLAPolicyCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating SLA policies"""
    class Meta:
        model = SLAPolicy
        fields = [
            'name', 'description', 'service', 'incident_category',
            'applies_to_priority', 'response_time', 'resolution_time',
            'coverage', 'is_active'
        ]
