"""
Workflow ViewSets - REST API viewsets for workflow management
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.workflows.models import Workflow, WorkflowStep, WorkflowInstance, WorkflowTransition
from apps.workflows.serializers import (
    WorkflowListSerializer, WorkflowDetailSerializer, WorkflowCreateUpdateSerializer,
    WorkflowStepSerializer, WorkflowInstanceSerializer, WorkflowTransitionSerializer
)


class WorkflowViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow management"""
    queryset = Workflow.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['workflow_type', 'organization']
    search_fields = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return WorkflowListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return WorkflowCreateUpdateSerializer
        return WorkflowDetailSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Workflow.objects.filter(is_active=True)
        return Workflow.objects.filter(organization_id=user.organization_id, is_active=True)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        """Get all steps for a workflow"""
        workflow = self.get_object()
        serializer = WorkflowStepSerializer(workflow.steps.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def instances(self, request, pk=None):
        """Get workflow instances for this workflow"""
        workflow = self.get_object()
        serializer = WorkflowInstanceSerializer(workflow.instances.all(), many=True)
        return Response(serializer.data)


class WorkflowStepViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow steps"""
    queryset = WorkflowStep.objects.all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow']
    ordering = ['id']


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow instances"""
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow', 'status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WorkflowTransitionViewSet(viewsets.ModelViewSet):
    """ViewSet for workflow transitions"""
    queryset = WorkflowTransition.objects.all()
    serializer_class = WorkflowTransitionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['workflow_instance', 'status']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
