"""
SLA ViewSets - REST API viewsets for SLA management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.sla.models import SLAPolicy, SLATarget, SLABreach, SLAEscalation, SLAMetric
from apps.sla.serializers import (
    SLAPolicyListSerializer, SLAPolicyDetailSerializer,
    SLAPolicyCreateUpdateSerializer, SLATargetSerializer,
    SLABreachSerializer, SLAEscalationSerializer, SLAMetricSerializer
)


class SLAPolicyViewSet(viewsets.ModelViewSet):
    """ViewSet for SLA policies"""
    queryset = SLAPolicy.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'service', 'coverage_type']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SLAPolicyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SLAPolicyCreateUpdateSerializer
        return SLAPolicyDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return SLAPolicy.objects.filter(is_active=True)
        return SLAPolicy.objects.filter(organization_id=user.organization_id, is_active=True)
    
    @action(detail=True, methods=['get'])
    def targets(self, request, pk=None):
        """Get all targets for an SLA policy"""
        policy = self.get_object()
        targets = policy.slatarget_set.all()
        serializer = SLATargetSerializer(targets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def breaches(self, request, pk=None):
        """Get all breaches for an SLA policy"""
        policy = self.get_object()
        breaches = policy.slabreach_set.all()
        serializer = SLABreachSerializer(breaches, many=True)
        return Response(serializer.data)


class SLATargetViewSet(viewsets.ModelViewSet):
    """ViewSet for SLA targets"""
    queryset = SLATarget.objects.all()
    serializer_class = SLATargetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sla_policy', 'severity']
    ordering = ['severity']


class SLABreachViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SLA breaches"""
    queryset = SLABreach.objects.all()
    serializer_class = SLABreachSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sla_policy', 'breach_type']
    ordering = ['-breached_at']


class SLAEscalationViewSet(viewsets.ModelViewSet):
    """ViewSet for SLA escalations"""
    queryset = SLAEscalation.objects.all()
    serializer_class = SLAEscalationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sla_policy', 'escalation_level']
    ordering = ['escalation_level']


class SLAMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SLA metrics"""
    queryset = SLAMetric.objects.all()
    serializer_class = SLAMetricSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['sla_policy']
    search_fields = ['metric_name']
