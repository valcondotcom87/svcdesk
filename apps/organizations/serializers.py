"""
Organizations Serializers
"""
from rest_framework import serializers
from apps.organizations.models import Department, DepartmentMember, ModuleCategory


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for departments"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'organization', 'name', 'description', 'parent', 'parent_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DepartmentMemberSerializer(serializers.ModelSerializer):
    """Serializer for department members"""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = DepartmentMember
        fields = ['id', 'department', 'department_name', 'user', 'user_name', 'role', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class ModuleCategorySerializer(serializers.ModelSerializer):
    """Serializer for module categories"""

    class Meta:
        model = ModuleCategory
        fields = [
            'id', 'organization', 'module', 'name', 'description',
            'is_active', 'sort_order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
