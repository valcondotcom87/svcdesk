"""
CMDB (Configuration Management Database) Serializers
"""
import re
from rest_framework import serializers
from apps.cmdb.models import (
    CICategory, ConfigurationItem as CI, CIAttribute, CIRelationship
)
from apps.organizations.models import Organization


class CICategorySerializer(serializers.ModelSerializer):
    """Serializer for CI categories"""
    ci_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CICategory
        fields = ['id', 'name', 'description', 'icon', 'ci_count']
    
    def get_ci_count(self, obj):
        return CI.objects.filter(category=obj).count()


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
    owner_team_name = serializers.CharField(source='owner_team.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CI
        fields = [
            'id', 'ci_number', 'name', 'category', 'category_name',
            'type', 'status', 'status_display', 'owner_team', 'owner_team_name',
            'serial_number', 'location'
        ]


class CIDetailSerializer(serializers.ModelSerializer):
    """Full CI detail serializer with nested relations"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    owner_name = serializers.CharField(source='owner_team.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Nested serializers
    attributes = CIAttributeValueSerializer(many=True, read_only=True)
    related_cis = CIRelationshipSerializer(many=True, read_only=True, source='outgoing_relationships')

    class Meta:
        model = CI
        fields = [
            'id', 'organization', 'ci_number', 'name', 'description', 'category', 'category_name',
            'type', 'status', 'status_display', 'owner_team', 'owner_name',
            'version', 'manufacturer', 'serial_number',
            'location', 'acquisition_date', 'disposal_date', 'warranty_expiry',
            'attributes', 'related_cis',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CICreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating CIs"""
    impact_analysis = serializers.CharField(required=False, allow_blank=True, write_only=True)
    dependency_analysis = serializers.CharField(required=False, allow_blank=True, write_only=True)
    estimated_downtime_minutes = serializers.IntegerField(required=False, write_only=True)
    estimated_users_impacted = serializers.IntegerField(required=False, write_only=True)
    relationship_target_id = serializers.UUIDField(required=False, write_only=True)
    relationship_type = serializers.ChoiceField(
        choices=[
            ('depends_on', 'Depends On'),
            ('supports', 'Supports'),
            ('connected_to', 'Connected To'),
            ('part_of', 'Part Of'),
            ('used_by', 'Used By'),
            ('installed_on', 'Installed On'),
        ],
        required=False,
        write_only=True,
    )

    class Meta:
        model = CI
        fields = [
            'ci_number', 'name', 'description', 'category', 'type', 'status',
            'version', 'manufacturer', 'serial_number', 'owner_team', 'location',
            'acquisition_date', 'disposal_date', 'warranty_expiry',
            'impact_analysis', 'dependency_analysis', 'estimated_downtime_minutes',
            'estimated_users_impacted', 'relationship_target_id', 'relationship_type'
        ]

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)

        request = self.context.get('request')
        org = None
        if request and getattr(request, 'user', None):
            user = request.user
            org = getattr(user, 'organization', None)
            if org is None and getattr(user, 'is_superuser', False):
                org = Organization.objects.filter(is_active=True).first()
        if org is None and instance is not None:
            org = instance.organization

        ci_number = attrs.get('ci_number') if 'ci_number' in attrs else getattr(instance, 'ci_number', '')
        category = attrs.get('category') if 'category' in attrs else getattr(instance, 'category', None)
        ci_type = attrs.get('type') if 'type' in attrs else getattr(instance, 'type', None)
        status = attrs.get('status') if 'status' in attrs else getattr(instance, 'status', None)
        owner_team = attrs.get('owner_team') if 'owner_team' in attrs else getattr(instance, 'owner_team', None)
        impact_analysis = attrs.get('impact_analysis') if 'impact_analysis' in attrs else ''
        dependency_analysis = attrs.get('dependency_analysis') if 'dependency_analysis' in attrs else ''
        estimated_downtime_minutes = attrs.get('estimated_downtime_minutes') if 'estimated_downtime_minutes' in attrs else None
        estimated_users_impacted = attrs.get('estimated_users_impacted') if 'estimated_users_impacted' in attrs else None
        relationship_target_id = attrs.get('relationship_target_id') if 'relationship_target_id' in attrs else None
        relationship_type = attrs.get('relationship_type') if 'relationship_type' in attrs else None

        normalized_ci_number = str(ci_number or '').strip().upper()
        if 'ci_number' in attrs:
            attrs['ci_number'] = normalized_ci_number

        errors = {}
        if 'ci_number' in attrs:
            if not normalized_ci_number or not re.match(r'^(?:[A-Z0-9]+-)*CI-\d{4,6}$', normalized_ci_number):
                errors['ci_number'] = 'CI number must follow format CI-0000 or ORG-CI-000000.'
        elif instance is None:
            if not normalized_ci_number or not re.match(r'^(?:[A-Z0-9]+-)*CI-\d{4,6}$', normalized_ci_number):
                errors['ci_number'] = 'CI number must follow format CI-0000 or ORG-CI-000000.'
        if not category:
            errors['category'] = 'Category is required for CMDB classification.'
        if not ci_type or not str(ci_type).strip():
            errors['type'] = 'CI type is required for CMDB classification.'
        if not status:
            errors['status'] = 'CI status is required for lifecycle tracking.'
        if not owner_team:
            errors['owner_team'] = 'Owner team is required for accountability.'

        requires_relationship = False
        if instance is None and org is not None:
            requires_relationship = CI.objects.filter(organization=org).exists()

        if instance is None:
            if not impact_analysis or not str(impact_analysis).strip():
                errors['impact_analysis'] = 'Impact analysis is required for ITIL CMDB registration.'
            if requires_relationship and (not relationship_target_id or not relationship_type):
                errors['relationship'] = 'A relationship target and type are required.'

        if relationship_target_id or relationship_type:
            if not relationship_target_id or not relationship_type:
                errors['relationship'] = 'Relationship target and type must be provided together.'
            else:
                target_qs = CI.objects.filter(id=relationship_target_id)
                if org is not None:
                    target_qs = target_qs.filter(organization=org)
                if not target_qs.exists():
                    errors['relationship_target_id'] = 'Relationship target CI was not found.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        impact_analysis = validated_data.pop('impact_analysis', '')
        dependency_analysis = validated_data.pop('dependency_analysis', '')
        estimated_downtime_minutes = validated_data.pop('estimated_downtime_minutes', None)
        estimated_users_impacted = validated_data.pop('estimated_users_impacted', None)
        relationship_target_id = validated_data.pop('relationship_target_id', None)
        relationship_type = validated_data.pop('relationship_type', None)

        ci = super().create(validated_data)

        if impact_analysis:
            CI.objects.filter(id=ci.id).update(impact_analysis=impact_analysis)
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='impact_analysis',
                defaults={'attribute_value': impact_analysis}
            )

        if dependency_analysis:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='dependency_analysis',
                defaults={'attribute_value': dependency_analysis}
            )

        if estimated_downtime_minutes is not None:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='estimated_downtime_minutes',
                defaults={'attribute_value': str(estimated_downtime_minutes)}
            )

        if estimated_users_impacted is not None:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='estimated_users_impacted',
                defaults={'attribute_value': str(estimated_users_impacted)}
            )

        if relationship_target_id and relationship_type:
            CIRelationship.objects.get_or_create(
                organization=ci.organization,
                source_ci=ci,
                target_ci_id=relationship_target_id,
                relationship_type=relationship_type,
            )

        return ci

    def update(self, instance, validated_data):
        impact_analysis = validated_data.pop('impact_analysis', None)
        dependency_analysis = validated_data.pop('dependency_analysis', None)
        estimated_downtime_minutes = validated_data.pop('estimated_downtime_minutes', None)
        estimated_users_impacted = validated_data.pop('estimated_users_impacted', None)
        relationship_target_id = validated_data.pop('relationship_target_id', None)
        relationship_type = validated_data.pop('relationship_type', None)

        ci = super().update(instance, validated_data)

        if impact_analysis is not None:
            CI.objects.filter(id=ci.id).update(impact_analysis=impact_analysis)
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='impact_analysis',
                defaults={'attribute_value': impact_analysis}
            )

        if dependency_analysis is not None:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='dependency_analysis',
                defaults={'attribute_value': dependency_analysis}
            )

        if estimated_downtime_minutes is not None:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='estimated_downtime_minutes',
                defaults={'attribute_value': str(estimated_downtime_minutes)}
            )

        if estimated_users_impacted is not None:
            CIAttribute.objects.update_or_create(
                ci=ci,
                attribute_name='estimated_users_impacted',
                defaults={'attribute_value': str(estimated_users_impacted)}
            )

        if relationship_target_id and relationship_type:
            CIRelationship.objects.get_or_create(
                organization=ci.organization,
                source_ci=ci,
                target_ci_id=relationship_target_id,
                relationship_type=relationship_type,
            )

        return ci
