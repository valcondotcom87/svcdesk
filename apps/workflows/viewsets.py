"""
Workflow ViewSets - REST API viewsets for workflow management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.workflows.models import Workflow, WorkflowState, WorkflowTransition, WorkflowExecution
from apps.workflows.serializers import (
    WorkflowListSerializer, WorkflowDetailSerializer, WorkflowCreateUpdateSerializer,
    WorkflowStateSerializer, WorkflowTransitionSerializer, WorkflowExecutionSerializer
)


class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow management"""
    queryset = Workflow.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['content_type']
    search_fields = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return WorkflowListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkflowCreateUpdateSerializer
        return WorkflowDetailSerializer
    
    @action(detail=True, methods=['get'])
    def states(self, request, pk=None):
        """Get all states for a workflow"""
        workflow = self.get_object()
        states = workflow.state_set.all()
        serializer = WorkflowStateSerializer(states, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def transitions(self, request, pk=None):
        """Get all transitions for a workflow"""
        workflow = self.get_object()
        transitions = workflow.transition_set.all()
        serializer = WorkflowTransitionSerializer(transitions, many=True)
        return Response(serializer.data)


class WorkflowStateViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow states"""
    queryset = WorkflowState.objects.all()
    serializer_class = WorkflowStateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow']
    ordering = ['id']


class WorkflowTransitionViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow transitions"""
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow', 'from_state', 'to_state']
    ordering = ['id']


class WorkflowExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for workflow executions"""
    queryset = WorkflowExecution.objects.all()
    serializer_class = WorkflowExecutionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow', 'is_completed']
    ordering = ['-started_at']
