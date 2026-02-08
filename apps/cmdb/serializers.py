"""
CMDB (Configuration Management Database) Serializers
"""
from rest_framework import serializers
from apps.cmdb.models import (
    CICategory, ConfigurationItem as CI, CIAttribute, CIRelationship
)


class CICategorySerializer(serializers.ModelSerializer):
    """Serializer for CI categories"""
    ci_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CICategory
        fields = ['id', 'name', 'description', 'icon', 'ci_count']
    
    def get_ci_count(self):
        return CI.objects.filter(category=self.instance).count()


class CIAttributeSerializer(serializers.ModelSerializer):
    """Serializer for CI attributes"""
    class Meta:
        model = CIAttribute
        fields = ['id', 'ci', 'attribute_name', 'attribute_value']


class CIAttributeValueSerializer(serializers.ModelSerializer):
    """Serializer for CI attribute values (alias of CIAttribute)"""
    class Meta:
        model = CIAttribute
        fields = ['id', 'ci', 'attribute_name', 'attribute_value']


class CIRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for CI relationships"""
    source_name = serializers.CharField(source='source_ci.name', read_only=True)
    target_name = serializers.CharField(source='target_ci.name', read_only=True)

    class Meta:
        model = CIRelationship
        fields = ['id', 'source_ci', 'source_name', 'target_ci', 'target_name', 'relationship_type', 'is_active']


class CIListSerializer(serializers.ModelSerializer):
    """Lightweight CI list serializer"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = CI
        fields = ['id', 'ci_number', 'name', 'category', 'category_name', 'serial_number', 'status', 'location']


class CIDetailSerializer(serializers.ModelSerializer):
    """Full CI detail serializer with nested relations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner_team.name', read_only=True)

    # Nested serializers
    attributes = CIAttributeValueSerializer(many=True, read_only=True, source='attributes')
    related_cis = CIRelationshipSerializer(many=True, read_only=True, source='outgoing_relationships')

    class Meta:
        model = CI
        fields = [
            'id', 'organization', 'ci_number', 'name', 'description', 'category', 'category_name',
            'serial_number', 'status', 'owner_team', 'owner_name',
            'location', 'attributes', 'related_cis',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CICreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating CIs"""
    class Meta:
        model = CI
        fields = [
            'ci_number', 'name', 'description', 'category', 'serial_number',
            'owner_team', 'location'
        ]
