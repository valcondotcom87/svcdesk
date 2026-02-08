"""
Workflow Serializers - REST API serializers for workflow management
"""
from rest_framework import serializers
from apps.workflows.models import Workflow, WorkflowState, WorkflowTransition, WorkflowExecution


class WorkflowStateSerializer(serializers.ModelSerializer):
    """Serializer for workflow states"""
    class Meta:
        model = WorkflowState
        fields = ['id', 'workflow', 'name', 'description', 'state_type', 'is_initial', 'is_final']


class WorkflowTransitionSerializer(serializers.ModelSerializer):
    """Serializer for workflow transitions"""
    from_state_name = serializers.CharField(source='from_state.name', read_only=True)
    to_state_name = serializers.CharField(source='to_state.name', read_only=True)
    
    class Meta:
        model = WorkflowTransition
        fields = [
            'id', 'workflow', 'from_state', 'from_state_name', 'to_state',
            'to_state_name', 'name', 'condition', 'action', 'requires_approval'
        ]


class WorkflowExecutionSerializer(serializers.ModelSerializer):
    """Serializer for workflow executions"""
    triggered_by_name = serializers.CharField(source='triggered_by.get_full_name', read_only=True)
    current_state_name = serializers.CharField(source='current_state.name', read_only=True)
    
    class Meta:
        model = WorkflowExecution
        fields = [
            'id', 'workflow', 'content_type', 'object_id', 'current_state',
            'current_state_name', 'triggered_by', 'triggered_by_name', 'execution_data',
            'is_completed', 'started_at', 'completed_at'
        ]


class WorkflowListSerializer(serializers.ModelSerializer):
    """Lightweight workflow list serializer"""
    model_type = serializers.CharField(source='content_type', read_only=True)
    
    class Meta:
        model = Workflow
        fields = ['id', 'name', 'description', 'model_type', 'is_active', 'created_at']


class WorkflowDetailSerializer(serializers.ModelSerializer):
    """Full workflow detail serializer with nested relations"""
    # Nested serializers
    states = WorkflowStateSerializer(many=True, read_only=True, source='state_set')
    transitions = WorkflowTransitionSerializer(many=True, read_only=True, source='transition_set')
    
    class Meta:
        model = Workflow
        fields = [
            'id', 'name', 'description', 'content_type', 'description_template',
            'states', 'transitions', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class WorkflowCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating workflows"""
    class Meta:
        model = Workflow
        fields = ['name', 'description', 'content_type', 'description_template', 'is_active']
