"""
Incident Serializers - REST API serializers for incident management
"""
from rest_framework import serializers
from apps.incidents.models import (
    Incident, IncidentComment, IncidentWorkaround, IncidentAttachment, IncidentMetric
)


class IncidentCommentSerializer(serializers.ModelSerializer):
    """Serializer for incident comments"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentComment
        fields = ['id', 'incident', 'text', 'is_internal', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']


class IncidentWorkaroundSerializer(serializers.ModelSerializer):
    """Serializer for incident workarounds"""
    class Meta:
        model = IncidentWorkaround
        fields = ['id', 'incident', 'title', 'description', 'effectiveness', 'created_at']


class IncidentAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for incident attachments"""
    class Meta:
        model = IncidentAttachment
        fields = ['id', 'incident', 'file', 'filename', 'file_type', 'file_size', 'created_at']


class IncidentMetricSerializer(serializers.ModelSerializer):
    """Serializer for incident metrics"""
    class Meta:
        model = IncidentMetric
        fields = [
            'id', 'incident', 'first_response_time_minutes', 'resolution_time_minutes',
            'total_time_minutes', 'mttr', 'mtta', 'fcr', 'customer_satisfaction',
            'created_at'
        ]


class IncidentListSerializer(serializers.ModelSerializer):
    """Lightweight incident list serializer"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'ticket_number', 'title', 'priority', 'priority_display', 'status', 'status_display',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name', 'sla_breach',
            'created_at', 'updated_at'
        ]


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Full incident detail serializer with nested relations"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_to_team_name = serializers.CharField(source='assigned_to_team.name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Nested serializers
    comments = IncidentCommentSerializer(many=True, read_only=True)
    workarounds = IncidentWorkaroundSerializer(many=True, read_only=True)
    attachments = IncidentAttachmentSerializer(many=True, read_only=True)
    metric = IncidentMetricSerializer(read_only=True, source='metric')
    
    class Meta:
        model = Incident
        fields = [
            'id', 'organization', 'ticket_number', 'title', 'description',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name',
            'assigned_to_team', 'assigned_to_team_name',
            'category', 'subcategory', 'affected_service',
            'priority', 'priority_display', 'urgency', 'urgency_display',
            'impact', 'impact_display',
            'status', 'status_display', 'resolution_code', 'resolution_notes',
            'first_response_time', 'resolved_at', 'closed_at',
            'sla_breach', 'sla_policy', 'sla_due_date', 'sla_escalated',
            'related_problem', 'change_request',
            'comments', 'workarounds', 'attachments', 'metric',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['ticket_number', 'created_at', 'updated_at']


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating incidents"""
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'category', 'subcategory', 'affected_service',
            'urgency', 'impact', 'requester', 'assigned_to', 'assigned_to_team'
        ]
    
    def create(self, validated_data):
        # Auto-calculate priority
        incident = Incident(**validated_data)
        incident.calculate_priority()
        
        # Generate ticket number
        org = validated_data.get('organization')
        count = Incident.objects.filter(organization=org).count()
        incident.ticket_number = f"{org.slug.upper()}-INC-{count + 1:05d}"
        
        incident.save()
        return incident


class IncidentActionSerializer(serializers.Serializer):
    """Serializer for incident actions (resolve, close, escalate)"""
    action = serializers.ChoiceField(choices=['resolve', 'close', 'reopen', 'escalate'])
    resolution_notes = serializers.CharField(required=False, allow_blank=True)
    resolution_code = serializers.CharField(required=False, allow_blank=True)
