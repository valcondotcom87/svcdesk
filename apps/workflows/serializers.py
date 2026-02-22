"""
Workflow Serializers - REST API serializers for workflow management
"""
from rest_framework import serializers
from apps.workflows.models import Workflow, WorkflowStep, WorkflowInstance, WorkflowTransition


class WorkflowStepSerializer(serializers.ModelSerializer):
    """Serializer for workflow steps"""
    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'workflow', 'step_number', 'name', 'description',
            'assigned_to_team', 'requires_approval', 'approval_count',
            'created_at', 'updated_at'
        ]


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for workflow transitions"""
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'workflow_instance', 'from_step', 'to_step',
            'status', 'notes', 'created_at'
        ]


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    """Serializer for workflow instances"""
    class Meta:
        model = WorkflowInstance
        fields = [
            'id', 'workflow', 'incident', 'service_request', 'change_request',
            'status', 'current_step',
            'completed_at', 'created_at', 'updated_at'
        ]


class WorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight workflow list serializer"""
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'workflow_type', 'is_active', 'created_at']


class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Full workflow detail serializer with nested relations"""
    steps = WorkflowStepSerializer(many=True, read_only=True)

    class Meta:
        model = Workflow
        fields = [
            'id', 'organization', 'name', 'description', 'workflow_type',
            'is_active', 'steps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkflowCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workflows"""
    class Meta:
        model = Workflow
        fields = ['name', 'description', 'workflow_type', 'is_active']
