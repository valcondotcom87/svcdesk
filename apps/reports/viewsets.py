"""
Report ViewSets - REST API viewsets for reporting and analytics
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.reports.models import (
    Report, ReportSchedule, ReportExecution, Dashboard, DashboardWidget
)
from apps.reports.serializers import (
    ReportListSerializer, ReportDetailSerializer, ReportCreateUpdateSerializer,
    ReportScheduleSerializer, ReportExecutionSerializer,
    DashboardListSerializer, DashboardDetailSerializer, DashboardCreateUpdateSerializer,
    DashboardWidgetSerializer
)


class ReportViewSet(viewsets.ModelViewSet):
    """ViewSet for reports"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'report_type', 'owner']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ReportListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ReportCreateUpdateSerializer
        return ReportDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Report.objects.all()
        return Report.objects.filter(organization_id=user.organization_id)
    
    def perform_create(self, serializer):
        """Set organization and owner"""
        serializer.save(organization=self.request.user.organization, owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """Execute a report"""
        report = self.get_object()
        
        try:
            execution = ReportExecution.objects.create(
                report=report,
                executed_by=request.user,
                status='running'
            )
            
            # TODO: Run actual report generation logic
            # For now, just mark as completed
            execution.status = 'completed'
            execution.completed_at = timezone.now()
            execution.save()
            
            serializer = ReportExecutionSerializer(execution)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def executions(self, request, pk=None):
        """Get execution history for a report"""
        report = self.get_object()
        executions = report.execution_set.all()
        serializer = ReportExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for report schedules"""
    queryset = ReportSchedule.objects.all()
    serializer_class = ReportScheduleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'is_active']
    ordering = ['next_run']


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for report executions"""
    queryset = ReportExecution.objects.all()
    serializer_class = ReportExecutionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'status']
    ordering = ['-completed_at']


class DashboardViewSet(viewsets.ModelViewSet):
    """ViewSet for dashboards"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'owner', 'is_default']
    search_fields = ['name', 'description']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DashboardListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DashboardCreateUpdateSerializer
        return DashboardDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Dashboard.objects.all()
        return Dashboard.objects.filter(organization_id=user.organization_id)
    
    def perform_create(self, serializer):
        """Set organization"""
        serializer.save(organization=self.request.user.organization)


class DashboardWidgetViewSet(viewsets.ModelViewSet):
    """ViewSet for dashboard widgets"""
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['dashboard', 'widget_type']
    ordering = ['position_y', 'position_x']
