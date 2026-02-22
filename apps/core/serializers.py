"""
Core Serializers - Shared serializers for all apps
"""
from rest_framework import serializers
from apps.organizations.models import Organization, Department, Team
from apps.users.models import CustomUser, UserRole, UserPermission


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization serializer"""
    user_count = serializers.SerializerMethodField()
    team_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'email', 'phone',
            'subscription_tier', 'is_active', 'created_at', 'updated_at',
            'user_count', 'team_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_user_count(self, obj):
        return obj.users.filter(is_active=True).count()
    
    def get_team_count(self, obj):
        return obj.teams.count()


class DepartmentSerializer(serializers.ModelSerializer):
    """Department serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Department
        fields = ['id', 'organization', 'organization_name', 'name', 'description', 'parent', 'created_at']
        read_only_fields = ['created_at']


class TeamSerializer(serializers.ModelSerializer):
    """Team serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = [
            'id', 'organization', 'organization_name', 'department', 'department_name',
            'name', 'description', 'manager', 'manager_name', 'member_count', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def get_member_count(self, obj):
        return obj.members.count()


class UserPermissionSerializer(serializers.ModelSerializer):
    """Permission serializer"""
    class Meta:
        model = UserPermission
        fields = ['id', 'module', 'action']


class UserRoleSerializer(serializers.ModelSerializer):
    """User role serializer with permissions"""
    permissions = UserPermissionSerializer(many=True, read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'organization', 'organization_name', 'name', 'description', 'is_default', 'permissions']


class UserListSerializer(serializers.ModelSerializer):
    """User list serializer (lightweight)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'user_type', 'is_active', 'organization', 'organization_name'
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    """User detail serializer (full)"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    roles = UserRoleSerializer(many=True, read_only=True, source='roles.all')
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'employee_id', 'phone', 'user_type', 'is_active', 'organization',
            'organization_name', 'roles', 'mfa_enabled', 'last_login',
            'date_joined', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']


class UserCreateUpdateSerializer(serializers.ModelSerializer):
    """User creation and update serializer"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password', 'password_confirm', 'first_name',
            'last_name', 'employee_id', 'phone', 'user_type', 'organization'
        ]
    
    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class AuditModelSerializer(serializers.ModelSerializer):
    """Serializer for AuditModel with user information"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    updated_by_username = serializers.CharField(source='updated_by.username', read_only=True)
    
    class Meta:
        fields = ['created_at', 'updated_at', 'created_by_username', 'updated_by_username']
