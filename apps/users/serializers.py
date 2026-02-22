"""
Users Serializers
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Organization, Team, TeamMember, Role, UserRole, ADSyncLog


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Organization serializer
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'domain', 'is_active', 
            'settings', 'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.filter(is_active=True).count()


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'full_name', 'phone', 'role', 'organization', 'organization_name',
            'is_active', 'is_verified', 'mfa_enabled', 'last_login',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserCreateSerializer(serializers.ModelSerializer):
    """
    User creation serializer with password
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role', 'organization'
        ]
    
    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User update serializer (without password)
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'role', 'is_active'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Password change serializer
    """
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
    def validate_old_password(self, value):
        """
        Validate old password
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class TeamSerializer(serializers.ModelSerializer):
    """
    Team serializer
    """
    team_lead_name = serializers.CharField(source='team_lead.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'name', 'description', 'organization', 
            'team_lead', 'team_lead_name', 'is_active',
            'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class TeamMemberSerializer(serializers.ModelSerializer):
    """
    Team member serializer
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'team', 'team_name', 'user', 'user_name', 
            'user_email', 'role', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']


class RoleSerializer(serializers.ModelSerializer):
    """
    Role serializer
    """
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'permissions', 
            'is_system_role', 'user_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_system_role']
    
    def get_user_count(self, obj):
        return obj.role_users.count()


class UserRoleSerializer(serializers.ModelSerializer):
    """
    User role assignment serializer
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.get_full_name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'user_name', 'role', 'role_name',
            'assigned_at', 'assigned_by', 'assigned_by_name'
        ]
        read_only_fields = ['id', 'assigned_at']


class ADSyncLogSerializer(serializers.ModelSerializer):
    """Serializer for AD sync history"""
    triggered_by_name = serializers.CharField(source='triggered_by.get_full_name', read_only=True)

    class Meta:
        model = ADSyncLog
        fields = [
            'id', 'started_at', 'completed_at', 'status',
            'created_count', 'updated_count', 'skipped_count',
            'error_message', 'source', 'triggered_by', 'triggered_by_name'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at']
