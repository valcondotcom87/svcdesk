"""
Incident Serializers - REST API serializers for incident management
"""
from datetime import timedelta
import os
from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.incidents.models import (
    Incident, IncidentComment, IncidentWorkaround, IncidentAttachment, IncidentMetric,
    IncidentCommunication
)
from apps.organizations.models import Organization
from apps.sla.utils import (
    apply_sla_dates,
    apply_sla_pause,
    resolve_sla_targets,
    select_sla_policy_for_incident,
    _priority_to_severity,
)


class IncidentCommentSerializer(serializers.ModelSerializer):
    """Serializer for incident comments"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = IncidentComment
        fields = ['id', 'incident', 'text', 'is_internal', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']

    def validate_text(self, value):
        if not str(value).strip():
            raise ValidationError('Comment text is required.')
        return value


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


class IncidentCommunicationSerializer(serializers.ModelSerializer):
    """Serializer for incident communications"""
    sent_by_name = serializers.CharField(source='sent_by.get_full_name', read_only=True)

    class Meta:
        model = IncidentCommunication
        fields = ['id', 'incident', 'channel', 'audience', 'message', 'sent_at', 'sent_by', 'sent_by_name']


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
            'id', 'ticket_number', 'title', 'category', 'priority', 'priority_display', 'status', 'status_display',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name', 'affected_service',
            'sla_breach', 'ola_breach', 'uc_breach', 'is_major', 'created_at', 'updated_at'
        ]


class IncidentDetailSerializer(serializers.ModelSerializer):
    """Full incident detail serializer with nested relations"""
    requester_name = serializers.CharField(source='requester.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    assigned_to_team_name = serializers.CharField(source='assigned_to_team.name', read_only=True)
    major_incident_manager_name = serializers.CharField(source='major_incident_manager.get_full_name', read_only=True)
    pir_owner_name = serializers.CharField(source='pir_owner.get_full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    urgency_display = serializers.CharField(source='get_urgency_display', read_only=True)
    impact_display = serializers.CharField(source='get_impact_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Nested serializers
    comments = IncidentCommentSerializer(many=True, read_only=True)
    workarounds = IncidentWorkaroundSerializer(many=True, read_only=True)
    attachments = IncidentAttachmentSerializer(many=True, read_only=True)
    metric = IncidentMetricSerializer(read_only=True)
    communications = IncidentCommunicationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'organization', 'ticket_number', 'title', 'description',
            'requester', 'requester_name', 'assigned_to', 'assigned_to_name',
            'assigned_to_team', 'assigned_to_team_name',
            'category', 'subcategory', 'affected_service',
            'priority', 'priority_display', 'urgency', 'urgency_display',
            'impact', 'impact_display',
            'status', 'status_display', 'is_major', 'major_incident_level',
            'escalation_status', 'major_incident_manager', 'major_incident_manager_name', 'communication_cadence_minutes',
            'next_communication_due', 'resolution_code', 'resolution_notes',
            'first_response_time', 'resolved_at', 'closed_at',
            'sla_breach', 'sla_policy', 'sla_coverage', 'sla_response_due_date', 'sla_response_breach',
            'sla_due_date', 'sla_escalated', 'sla_paused_at', 'sla_pause_total_minutes',
            'ola_target_minutes', 'uc_target_minutes', 'ola_due_date', 'uc_due_date',
            'ola_breach', 'uc_breach',
            'pir_required', 'pir_status', 'pir_summary', 'pir_notes',
            'pir_owner', 'pir_owner_name', 'pir_completed_at',
            'related_problem', 'change_request',
            'comments', 'workarounds', 'attachments', 'communications', 'metric',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['ticket_number', 'created_at', 'updated_at']


class IncidentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating incidents"""
    class Meta:
        model = Incident
        fields = [
            'title', 'description', 'category', 'subcategory', 'affected_service',
            'urgency', 'impact', 'requester', 'assigned_to', 'assigned_to_team',
            'sla_policy', 'is_major', 'major_incident_level', 'major_incident_manager',
            'escalation_status', 'communication_cadence_minutes', 'ola_target_minutes', 'uc_target_minutes',
            'pir_required', 'pir_status', 'pir_summary', 'pir_notes', 'pir_owner', 'pir_completed_at'
        ]
        extra_kwargs = {
            'category': {'required': False, 'allow_blank': True},
            'subcategory': {'required': False, 'allow_blank': True},
            'affected_service': {'required': False, 'allow_blank': True},
            'requester': {'required': False, 'allow_null': True},
            'assigned_to': {'required': False, 'allow_null': True},
            'assigned_to_team': {'required': False, 'allow_null': True},
            'sla_policy': {'required': False, 'allow_null': True},
            'major_incident_manager': {'required': False, 'allow_null': True},
            'communication_cadence_minutes': {'required': False},
            'ola_target_minutes': {'required': False, 'allow_null': True},
            'uc_target_minutes': {'required': False, 'allow_null': True},
            'pir_required': {'required': False},
            'pir_status': {'required': False},
            'pir_summary': {'required': False, 'allow_blank': True},
            'pir_notes': {'required': False, 'allow_blank': True},
            'pir_owner': {'required': False, 'allow_null': True},
            'pir_completed_at': {'required': False, 'allow_null': True},
        }

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        org = self._resolve_org(attrs, instance)
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        category = attrs.get('category') if 'category' in attrs else getattr(instance, 'category', '')
        if not category or not str(category).strip():
            raise ValidationError({'category': 'Category is required for ITIL incident classification.'})

        urgency = attrs.get('urgency') if 'urgency' in attrs else getattr(instance, 'urgency', None)
        impact = attrs.get('impact') if 'impact' in attrs else getattr(instance, 'impact', None)
        if urgency is None or impact is None:
            raise ValidationError({'priority': 'Impact and urgency are required for ITIL prioritization.'})

        is_major = attrs.get('is_major') if 'is_major' in attrs else getattr(instance, 'is_major', False)
        if is_major is None:
            is_major = False
            attrs['is_major'] = False
        major_level = attrs.get('major_incident_level') if 'major_incident_level' in attrs else getattr(instance, 'major_incident_level', None)
        if is_major and not major_level:
            raise ValidationError({'major_incident_level': 'Major incident level is required when marked as major.'})

        major_manager = attrs.get('major_incident_manager') if 'major_incident_manager' in attrs else getattr(instance, 'major_incident_manager', None)
        if is_major and not major_manager:
            raise ValidationError({'major_incident_manager': 'Major incident manager is required for major incidents.'})

        if not is_major and 'major_incident_level' in attrs:
            attrs['major_incident_level'] = None

        cadence = attrs.get('communication_cadence_minutes') if 'communication_cadence_minutes' in attrs else getattr(instance, 'communication_cadence_minutes', None)
        if is_major and (cadence is None or cadence <= 0):
            raise ValidationError({'communication_cadence_minutes': 'Communication cadence must be set for major incidents.'})

        pir_required = attrs.get('pir_required') if 'pir_required' in attrs else getattr(instance, 'pir_required', False)
        pir_status = attrs.get('pir_status') if 'pir_status' in attrs else getattr(instance, 'pir_status', None)
        if is_major:
            attrs['pir_required'] = True
            if not pir_status or pir_status == 'not_required':
                attrs['pir_status'] = 'pending'
        else:
            if not pir_required:
                attrs['pir_status'] = 'not_required'
            elif pir_required and not pir_status:
                attrs['pir_status'] = 'pending'

        requester = attrs.get('requester') if 'requester' in attrs else getattr(instance, 'requester', None)
        if user and user.role == 'end_user' and requester and requester.id != user.id:
            raise ValidationError({'requester': 'End users can only set themselves as requester.'})

        if user and user.role == 'end_user' and attrs.get('assigned_to') is not None:
            raise ValidationError({'assigned_to': 'End users cannot assign incidents.'})

        for field_name in ['requester', 'assigned_to', 'major_incident_manager', 'pir_owner']:
            value = attrs.get(field_name) if field_name in attrs else getattr(instance, field_name, None)
            self._validate_user_org(value, org, field_name)

        assigned_team = attrs.get('assigned_to_team') if 'assigned_to_team' in attrs else getattr(instance, 'assigned_to_team', None)
        self._validate_team_org(assigned_team, org, 'assigned_to_team')

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

    def _validate_team_org(self, team, org, field_name):
        if not team or not org:
            return
        if team.organization_id != org.id:
            raise ValidationError({field_name: 'Team must belong to the same organization.'})

    def _validate_policy_org(self, policy, org, field_name):
        if not policy or not org:
            return
        if getattr(policy, 'organization_id', None) != org.id:
            raise ValidationError({field_name: 'SLA policy must belong to the same organization.'})

    def _apply_ola_uc_targets(self, incident, force=False):
        now = timezone.now()
        updated_fields = []

        if incident.ola_target_minutes:
            if force or incident.ola_due_date is None:
                base_time = now if force and incident.created_at else incident.created_at or now
                incident.ola_due_date = base_time + timedelta(minutes=incident.ola_target_minutes)
                updated_fields.append('ola_due_date')
        elif force and incident.ola_due_date:
            incident.ola_due_date = None
            updated_fields.append('ola_due_date')

        if incident.uc_target_minutes:
            if force or incident.uc_due_date is None:
                base_time = now if force and incident.created_at else incident.created_at or now
                incident.uc_due_date = base_time + timedelta(minutes=incident.uc_target_minutes)
                updated_fields.append('uc_due_date')
        elif force and incident.uc_due_date:
            incident.uc_due_date = None
            updated_fields.append('uc_due_date')

        if incident.update_breach_status(now=now):
            updated_fields.extend(['ola_breach', 'uc_breach'])

        if updated_fields:
            incident.save(update_fields=sorted(set(updated_fields)))
    
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
                raise ValidationError({'organization': 'Organization is required to create an incident.'})
            validated_data['organization'] = org

        # Auto-calculate priority
        incident = Incident(**validated_data)
        incident.calculate_priority()
        
        # Generate ticket number
        count = Incident.objects.filter(organization=org).count()
        incident.ticket_number = f"{org.slug.upper()}-INC-{count + 1:05d}"
        
        incident.save()
        if not incident.sla_policy:
            policy = select_sla_policy_for_incident(incident)
            if policy:
                incident.sla_policy = policy
                if incident.priority == 1 or incident.impact == 1:
                    incident.sla_coverage = '24x7'
                else:
                    incident.sla_coverage = policy.coverage
                severity = _priority_to_severity(incident.priority, is_incident=True)
                response_minutes, resolution_minutes = resolve_sla_targets(policy, severity)
                updated = ['sla_policy', 'sla_coverage']
                updated.extend(apply_sla_dates(incident, response_minutes, resolution_minutes, incident.created_at))
                incident.save(update_fields=sorted(set(updated)))
        if incident.pir_status == 'completed' and not incident.pir_completed_at:
            incident.pir_completed_at = timezone.now()
            incident.save(update_fields=['pir_completed_at'])
        self._apply_ola_uc_targets(incident, force=True)
        return incident

    def update(self, instance, validated_data):
        previous_status = instance.status
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if 'pir_status' in validated_data:
            if instance.pir_status == 'completed' and not instance.pir_completed_at:
                instance.pir_completed_at = timezone.now()
            if instance.pir_status != 'completed' and instance.pir_completed_at:
                instance.pir_completed_at = None

        if 'impact' in validated_data or 'urgency' in validated_data:
            instance.calculate_priority()

        if instance.first_response_time is None and instance.status in ['acknowledged', 'assigned', 'in_progress']:
            instance.first_response_time = timezone.now()

        instance.save()
        pause_fields = []
        pause_fields.extend(apply_sla_pause(instance, instance.status == 'on_hold'))
        if pause_fields:
            instance.save(update_fields=sorted(set(pause_fields)))
        if 'ola_target_minutes' in validated_data or 'uc_target_minutes' in validated_data:
            self._apply_ola_uc_targets(instance, force=True)
        else:
            self._apply_ola_uc_targets(instance, force=False)
        if not instance.sla_policy:
            policy = select_sla_policy_for_incident(instance)
            if policy:
                instance.sla_policy = policy
                if instance.priority == 1 or instance.impact == 1:
                    instance.sla_coverage = '24x7'
                else:
                    instance.sla_coverage = policy.coverage
                severity = _priority_to_severity(instance.priority, is_incident=True)
                response_minutes, resolution_minutes = resolve_sla_targets(policy, severity)
                updated = ['sla_policy', 'sla_coverage']
                updated.extend(apply_sla_dates(instance, response_minutes, resolution_minutes, instance.created_at))
                instance.save(update_fields=sorted(set(updated)))
        return instance


class IncidentActionSerializer(serializers.Serializer):
    """Serializer for incident actions (resolve, close, escalate)"""
    action = serializers.ChoiceField(choices=['resolve', 'close', 'reopen', 'escalate'])
    resolution_notes = serializers.CharField(required=False, allow_blank=True)
    resolution_code = serializers.CharField(required=False, allow_blank=True)
