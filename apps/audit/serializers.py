"""
Audit serializers
"""
from rest_framework import serializers
from apps.audit.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'organization', 'organization_name', 'user', 'user_name',
            'action', 'entity_type', 'entity_id', 'field_name', 'old_value',
            'new_value', 'ip_address', 'user_agent', 'status', 'error_message',
            'created_at'
        ]
        read_only_fields = ['created_at']
