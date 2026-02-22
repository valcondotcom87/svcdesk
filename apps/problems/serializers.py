"""
Problem Management Serializers - REST API serializers for problem management
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from apps.problems.models import Problem, RootCauseAnalysis, KnownErrorDatabase as KEDB
from apps.organizations.models import Organization


class RCASerializer(serializers.ModelSerializer):
    """Serializer for Root Cause Analysis"""

    class Meta:
        model = RootCauseAnalysis
        fields = [
            'id', 'problem', 'investigation_method', 'five_whys',
            'contributing_factors', 'lessons_learned', 'created_at', 'updated_at'
        ]


class KEDBSerializer(serializers.ModelSerializer):
    """Serializer for Known Error Database entries"""

    class Meta:
        model = KEDB
        fields = [
            'id', 'organization', 'problem', 'title', 'description', 'error_code',
            'symptoms', 'workaround', 'permanent_solution', 'resolution_rate',
            'created_at', 'updated_at'
        ]


class ProblemListSerializer(serializers.ModelSerializer):
    """Lightweight problem list serializer"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Problem
        fields = [
            'id', 'ticket_number', 'title', 'category', 'owner', 'owner_name',
            'status', 'status_display', 'created_at'
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Full problem detail serializer with nested relations"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    rca = RCASerializer(read_only=True, source='rca')
    kedb_entry = KEDBSerializer(read_only=True, source='kedb_entry')

    class Meta:
        model = Problem
        fields = [
            'id', 'organization', 'ticket_number', 'title', 'description', 'category',
            'owner', 'owner_name', 'status', 'status_display',
            'affected_users', 'affected_services',
            'root_cause', 'workaround', 'permanent_solution',
            'first_incident_date', 'identified_date', 'resolved_date',
            'change_request', 'rca', 'kedb_entry',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['ticket_number', 'created_at', 'updated_at']


class ProblemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating problems"""

    class Meta:
        model = Problem
        fields = [
            'title', 'description', 'category', 'owner', 'status',
            'affected_users', 'affected_services',
            'root_cause', 'workaround', 'permanent_solution',
            'first_incident_date', 'identified_date', 'resolved_date',
            'change_request'
        ]
        extra_kwargs = {
            'category': {'required': False, 'allow_blank': True},
            'owner': {'required': False, 'allow_null': True},
        }

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
                raise ValidationError({'organization': 'Organization is required to create a problem.'})
            validated_data['organization'] = org
        count = Problem.objects.filter(organization=org).count()
        validated_data['ticket_number'] = f"{org.slug.upper()}-PRB-{count + 1:05d}"
        return super().create(validated_data)

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        status = attrs.get('status') if 'status' in attrs else getattr(instance, 'status', None)
        root_cause = attrs.get('root_cause') if 'root_cause' in attrs else getattr(instance, 'root_cause', '')
        permanent_solution = attrs.get('permanent_solution') if 'permanent_solution' in attrs else getattr(instance, 'permanent_solution', '')

        if status in ['resolved', 'closed']:
            if not root_cause or not str(root_cause).strip():
                raise ValidationError({'root_cause': 'Root cause is required before resolving a problem.'})
            if not permanent_solution or not str(permanent_solution).strip():
                raise ValidationError({'permanent_solution': 'Permanent solution is required before resolving a problem.'})
            if instance is not None and not hasattr(instance, 'rca'):
                raise ValidationError({'rca': 'Root cause analysis record is required before resolving a problem.'})

        return attrs
