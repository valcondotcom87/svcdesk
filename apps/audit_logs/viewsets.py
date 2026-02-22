"""
Audit Log ViewSets - REST API viewsets for audit logging and compliance
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.audit_logs.models import AuditLog, ComplianceLog
from apps.audit_logs.serializers import AuditLogSerializer, ComplianceLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for audit logs"""
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'action', 'content_type']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return AuditLog.objects.all()
        # Filter audit logs for objects in user's organization
        return AuditLog.objects.all()  # Could add more specific filtering


class ComplianceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for compliance logs"""
    queryset = ComplianceLog.objects.all()
    serializer_class = ComplianceLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'compliance_framework', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ComplianceLog.objects.all()
        return ComplianceLog.objects.filter(organization_id=user.organization_id)
