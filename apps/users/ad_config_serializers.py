"""
Active Directory Configuration Serializer
"""
from rest_framework import serializers
from apps.users.ad_config import ADConfiguration


class ADConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for AD configuration"""
    
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )
    is_configured = serializers.BooleanField(read_only=True)
    connection_string = serializers.CharField(read_only=True)
    last_sync_status_display = serializers.CharField(
        source='get_last_sync_status_display',
        read_only=True
    )
    
    class Meta:
        model = ADConfiguration
        fields = [
            'id', 'organization', 'organization_name',
            'server_name', 'server_port', 'use_ssl',
            'bind_username', 'bind_password',
            'search_base', 'search_filter',
            'username_attribute', 'email_attribute',
            'first_name_attribute', 'last_name_attribute',
            'phone_attribute',
            'group_base', 'group_member_attribute',
            'auto_create_users', 'auto_update_users',
            'auto_disable_missing_users',
            'is_enabled',
            'last_sync_at', 'last_sync_status', 'last_sync_status_display',
            'last_sync_error',
            'is_configured', 'connection_string',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'last_sync_at', 'last_sync_status',
            'last_sync_error', 'created_at', 'updated_at',
            'is_configured', 'connection_string'
        ]
        extra_kwargs = {
            'bind_password': {
                'write_only': True,
                'help_text': 'Service account password (write-only)'
            }
        }
    
    def validate(self, data):
        """Validate AD configuration"""
        if not data.get('server_name'):
            raise serializers.ValidationError("Server name is required")
        
        if not data.get('bind_username'):
            raise serializers.ValidationError("Bind username is required")
        
        if not data.get('bind_password'):
            raise serializers.ValidationError("Bind password is required")
        
        if not data.get('search_base'):
            raise serializers.ValidationError("Search base DN is required")
        
        return data
