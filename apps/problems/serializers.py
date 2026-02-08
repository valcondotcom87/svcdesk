"""
Problem Management Serializers - REST API serializers for problem management
"""
from rest_framework import serializers
from apps.problems.models import Problem, RootCauseAnalysis, KnownErrorDatabase as KEDB


class RCASerializer(serializers.ModelSerializer):
    """Serializer for Root Cause Analysis"""
    class Meta:
        model = RootCauseAnalysis
        fields = [
            'id', 'problem', 'investigation_method', 'five_whys', 'contributing_factors',
            'lessons_learned', 'created_at', 'updated_at'
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
            'id', 'problem_number', 'title', 'owner', 'owner_name',
            'status', 'status_display', 'related_incident_count', 'created_at'
        ]


class ProblemDetailSerializer(serializers.ModelSerializer):
    """Full problem detail serializer with nested relations"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    # Nested serializers
    rca = RCASerializer(read_only=True, source='rootcauseanalysis_set')
    kedb = KEDBSerializer(read_only=True, source='kedb_set')
    
    class Meta:
        model = Problem
        fields = [
            'id', 'organization', 'problem_number', 'title', 'description',
            'owner', 'owner_name', 'status', 'status_display',
            'priority', 'priority_display', 'category', 'impact_scope',
            'temporary_fix', 'workaround_available',
            'investigation_status', 'investigation_due_date',
            'related_incident_count', 'related_change',
            'rca', 'kedb',
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]
        read_only_fields = ['problem_number', 'created_at', 'updated_at']


class ProblemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating problems"""
    class Meta:
        model = Problem
        fields = [
            'title', 'description', 'category', 'owner', 'priority',
            'impact_scope', 'temporary_fix', 'workaround_available'
        ]
    
    def create(self, validated_data):
        # Generate problem number
        org = validated_data.get('organization')
        count = Problem.objects.filter(organization=org).count()
        validated_data['problem_number'] = f"{org.slug.upper()}-PRB-{count + 1:05d}"
        
        return super().create(validated_data)
