from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import (
    ComplianceFramework, ComplianceRequirement, ImmutableAuditLog,
    IncidentResponsePlan, VulnerabilityTracking, ComplianceCheckpoint
)
from .serializers import (
    ComplianceFrameworkSerializer, ComplianceRequirementSerializer,
    ImmutableAuditLogSerializer, IncidentResponsePlanSerializer,
    VulnerabilityTrackingSerializer, ComplianceCheckpointSerializer
)


class ComplianceFrameworkViewSet(viewsets.ModelViewSet):
    """
    CRUD operations untuk Compliance Frameworks (ISO 27001, NIST, GDPR, etc)
    """
    queryset = ComplianceFramework.objects.all()
    serializer_class = ComplianceFrameworkSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['framework', 'description']
    ordering_fields = ['framework', 'status', 'progress_percentage', 'created_at']
    ordering = ['-updated_at']

    @action(detail=False, methods=['get'])
    def compliance_summary(self, request):
        """Get overall compliance status summary"""
        frameworks = self.get_queryset()
        total = frameworks.count()
        certified = frameworks.filter(status='certified').count()
        in_progress = frameworks.filter(status='in_progress').count()

        summary = {
            'total_frameworks': total,
            'certified': certified,
            'in_progress': in_progress,
            'planned': frameworks.filter(status='planned').count(),
            'average_progress': frameworks.aggregate(
                avg_progress=models.Avg('progress_percentage')
            )['avg_progress'] or 0,
            'frameworks': self.get_serializer(frameworks, many=True).data
        }
        return Response(summary)

    @action(detail=True, methods=['get'])
    def requirements_status(self, request, pk=None):
        """Get detailed requirements status for a framework"""
        framework = self.get_object()
        requirements = framework.requirements.all()
        
        status_breakdown = {
            'total': requirements.count(),
            'not_started': requirements.filter(status='not_started').count(),
            'in_progress': requirements.filter(status='in_progress').count(),
            'implemented': requirements.filter(status='implemented').count(),
            'verified': requirements.filter(status='verified').count(),
        }
        
        return Response({
            'framework': self.get_serializer(framework).data,
            'status_breakdown': status_breakdown,
            'requirements': ComplianceRequirementSerializer(requirements, many=True).data
        })


class ComplianceRequirementViewSet(viewsets.ModelViewSet):
    """
    Manage individual compliance requirements
    """
    queryset = ComplianceRequirement.objects.all()
    serializer_class = ComplianceRequirementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['requirement_id', 'title', 'description']
    ordering_fields = ['requirement_id', 'status', 'due_date']

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue requirements"""
        overdue_reqs = self.get_queryset().filter(
            due_date__lt=timezone.now().date(),
            status__in=['not_started', 'in_progress']
        )
        serializer = self.get_serializer(overdue_reqs, many=True)
        return Response(serializer.data)


class ImmutableAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View tamper-proof audit logs (compliance requirement)
    """
    queryset = ImmutableAuditLog.objects.all()
    serializer_class = ImmutableAuditLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__email', 'action', 'object_repr']
    ordering_fields = ['timestamp', 'severity', 'action']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'])
    def by_user(self, request):
        """Get audit logs by specific user"""
        user_id = request.query_params.get('user_id')
        if user_id:
            logs = self.get_queryset().filter(user_id=user_id)
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        return Response({'error': 'user_id parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def by_action(self, request):
        """Get audit logs by action type"""
        action_type = request.query_params.get('action')
        if action_type:
            logs = self.get_queryset().filter(action=action_type)
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        return Response({'error': 'action parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def critical_events(self, request):
        """Get critical severity audit events"""
        critical_logs = self.get_queryset().filter(
            severity__in=['high', 'critical']
        )[:100]
        serializer = self.get_serializer(critical_logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def verify_chain_integrity(self, request):
        """Verify hash chain integrity of audit logs"""
        logs = self.get_queryset().order_by('timestamp')
        chain_valid = True
        issues = []

        for i, log in enumerate(logs):
            if not log.hash_chain_valid:
                chain_valid = False
                issues.append({
                    'log_id': log.id,
                    'timestamp': log.timestamp,
                    'issue': 'Hash chain integrity compromised'
                })

        return Response({
            'total_logs': self.get_queryset().count(),
            'chain_valid': chain_valid,
            'integrity_issues': issues
        })


class IncidentResponsePlanViewSet(viewsets.ModelViewSet):
    """
    Manage incident response plans (ISO 27035, NIST IR)
    """
    queryset = IncidentResponsePlan.objects.all()
    serializer_class = IncidentResponsePlanSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'incident_type', 'description']
    ordering_fields = ['severity', 'last_reviewed', 'created_at']

    @action(detail=True, methods=['get'])
    def test_plan(self, request, pk=None):
        """Get procedure for testing this incident response plan"""
        plan = self.get_object()
        return Response({
            'plan': self.get_serializer(plan).data,
            'testing_procedure': [
                f"1. Review {plan.name}",
                f"2. Verify detection procedures: {plan.detection_procedures[:100]}...",
                f"3. Simulate initial response: {plan.initial_response[:100]}...",
                f"4. Test escalation path with {plan.escalation_path[:50]}...",
                f"5. Document results and gaps"
            ]
        })

    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Get plans by severity level"""
        severity = request.query_params.get('severity')
        if severity:
            plans = self.get_queryset().filter(severity=severity)
            serializer = self.get_serializer(plans, many=True)
            return Response(serializer.data)
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @action(detail=False, methods=['get'])
    def review_due(self, request):
        """Get plans due for review"""
        due_plans = self.get_queryset().filter(
            next_review_date__lte=timezone.now().date()
        )
        serializer = self.get_serializer(due_plans, many=True)
        return Response(serializer.data)


class VulnerabilityTrackingViewSet(viewsets.ModelViewSet):
    """
    Track and manage vulnerabilities (NIST, ISO 27001)
    """
    queryset = VulnerabilityTracking.objects.all()
    serializer_class = VulnerabilityTrackingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['vulnerability_id', 'title', 'affected_system', 'cve_reference']
    ordering_fields = ['discovery_date', 'severity', 'status', 'target_remediation_date']

    @action(detail=False, methods=['get'])
    def open_vulnerabilities(self, request):
        """Get all open vulnerabilities"""
        open_vulns = self.get_queryset().filter(
            status__in=['open', 'acknowledged', 'in_progress']
        )
        serializer = self.get_serializer(open_vulns, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue_remediations(self, request):
        """Get vulnerabilities overdue for remediation"""
        overdue = self.get_queryset().filter(
            target_remediation_date__lt=timezone.now().date(),
            status__in=['open', 'acknowledged', 'in_progress']
        )
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        """Get vulnerabilities grouped by severity"""
        severity = request.query_params.get('severity')
        if severity:
            vulns = self.get_queryset().filter(severity=severity)
        else:
            vulns = self.get_queryset()

        severity_counts = vulns.values('severity').annotate(count=Count('id'))
        return Response({
            'severity_breakdown': severity_counts,
            'vulnerabilities': self.get_serializer(vulns, many=True).data
        })

    @action(detail=False, methods=['get'])
    def remediation_report(self, request):
        """Get remediation metrics and report"""
        vulns = self.get_queryset()
        
        report = {
            'total': vulns.count(),
            'open': vulns.filter(status='open').count(),
            'in_progress': vulns.filter(status='in_progress').count(),
            'resolved': vulns.filter(status='resolved').count(),
            'critical': vulns.filter(severity='critical').count(),
            'average_time_to_resolve': 'TBD',  # Calculate based on actual dates
            'remediation_compliance': {
                'on_schedule': vulns.filter(
                    actual_remediation_date__lte=models.F('target_remediation_date')
                ).count(),
                'overdue': vulns.filter(
                    status__in=['open', 'in_progress'],
                    target_remediation_date__lt=timezone.now().date()
                ).count(),
            }
        }
        return Response(report)


class ComplianceCheckpointViewSet(viewsets.ModelViewSet):
    """
    Manage compliance checkpoints and assessments
    """
    queryset = ComplianceCheckpoint.objects.all()
    serializer_class = ComplianceCheckpointSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'checkpoint_type', 'description']
    ordering_fields = ['planned_date', 'compliance_score', 'status']

    @action(detail=False, methods=['get'])
    def pending_checkpoints(self, request):
        """Get checkpoints that need to be completed"""
        pending = self.get_queryset().filter(
            status__in=['planned', 'in_progress'],
            planned_date__lte=timezone.now().date()
        )
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def compliance_score(self, request):
        """Get overall compliance score"""
        checkpoints = self.get_queryset().filter(status='completed')
        
        if checkpoints.count() > 0:
            avg_score = checkpoints.aggregate(
                avg_score=models.Avg('compliance_score')
            )['avg_score']
            
            recent_5 = checkpoints.order_by('-actual_completion_date')[:5]
            return Response({
                'overall_compliance_score': round(avg_score, 2),
                'total_completed': checkpoints.count(),
                'recent_checkpoints': self.get_serializer(recent_5, many=True).data
            })
        return Response({
            'overall_compliance_score': 0,
            'total_completed': 0,
            'message': 'No completed checkpoints yet'
        })

    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        """Mark checkpoint as completed"""
        checkpoint = self.get_object()
        checkpoint.status = 'completed'
        checkpoint.actual_completion_date = timezone.now().date()
        checkpoint.save()
        
        return Response({
            'message': 'Checkpoint marked as complete',
            'checkpoint': self.get_serializer(checkpoint).data
        })


# Import statement for models in viewsets (fix circular import)
from django.db import models as db_models
