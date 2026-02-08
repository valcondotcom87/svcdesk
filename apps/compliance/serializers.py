from rest_framework import serializers
from .models import (
    ComplianceFramework, ComplianceRequirement, ImmutableAuditLog,
    IncidentResponsePlan, VulnerabilityTracking, ComplianceCheckpoint
)


class ComplianceRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplianceRequirement
        fields = [
            'id', 'requirement_id', 'title', 'description', 'status',
            'implementation_evidence', 'due_date', 'completion_date',
            'risk_if_not_implemented', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ComplianceFrameworkSerializer(serializers.ModelSerializer):
    requirements = ComplianceRequirementSerializer(many=True, read_only=True)
    requirement_count = serializers.SerializerMethodField()
    implemented_count = serializers.SerializerMethodField()

    class Meta:
        model = ComplianceFramework
        fields = [
            'id', 'framework', 'description', 'status', 'version',
            'target_date', 'certification_date', 'expiry_date',
            'progress_percentage', 'requirements', 'requirement_count',
            'implemented_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_requirement_count(self, obj):
        return obj.requirements.count()

    def get_implemented_count(self, obj):
        return obj.requirements.filter(status='verified').count()


class ImmutableAuditLogSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ImmutableAuditLog
        fields = [
            'id', 'action', 'user', 'timestamp',
            'content_type', 'object_id', 'object_repr',
            'changes_made', 'ip_address', 'severity',
            'data_hash', 'hash_chain_valid', 'description',
            'approval_status'
        ]
        read_only_fields = [
            'timestamp', 'data_hash', 'hash_chain_valid', 'previous_hash'
        ]


class IncidentResponsePlanSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = IncidentResponsePlan
        fields = [
            'id', 'name', 'description', 'incident_type', 'severity', 'status',
            'detection_procedures', 'initial_response', 'escalation_path',
            'investigation_steps', 'recovery_procedures', 'communication_template',
            'post_incident_review', 'primary_contact',
            'sla_detection', 'sla_response', 'sla_resolution',
            'version', 'last_reviewed', 'next_review_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_reviewed']


class VulnerabilityTrackingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = VulnerabilityTracking
        fields = [
            'id', 'vulnerability_id', 'title', 'description', 'affected_system',
            'severity', 'status', 'discovery_date', 'discovered_by', 'scan_tool',
            'cve_reference', 'business_impact', 'remediation_effort',
            'remediation_plan', 'responsible_person',
            'target_remediation_date', 'actual_remediation_date',
            'risk_acceptance_justification', 'accepted_by',
            'acceptance_date', 'acceptance_expiry', 'internal_notes',
            'verification_steps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'discovery_date']


class ComplianceCheckpointSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ComplianceCheckpoint
        fields = [
            'id', 'checkpoint_type', 'name', 'description', 'frameworks',
            'status', 'planned_date', 'actual_completion_date',
            'frequency', 'assigned_to', 'findings',
            'issues_identified', 'issues_resolved', 'compliance_score',
            'evidence_attached', 'remediation_required', 'remediation_deadline',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
