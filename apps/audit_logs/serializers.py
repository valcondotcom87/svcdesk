"""
Audit Log Serializers - REST API serializers for audit logging and compliance
"""
from rest_framework import serializers
from apps.audit_logs.models import AuditLog, ComplianceLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit logs"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'action_display',
            'content_type', 'object_id', 'object_name', 'old_values', 'new_values',
            'ip_address', 'user_agent', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class ComplianceLogSerializer(serializers.ModelSerializer):
    """Serializer for compliance logs"""
    triggered_by_name = serializers.CharField(source='triggered_by.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ComplianceLog
        fields = [
            'id', 'organization', 'compliance_framework', 'audit_log',
            'triggered_by', 'triggered_by_name', 'status', 'status_display',
            'findings', 'remediation_actions', 'created_at'
        ]
