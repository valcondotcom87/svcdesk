"""
REST API URL Configuration - API v1
Main router configuration for all ViewSets
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response

# Import ViewSets from all apps
from apps.core.viewsets import (
    OrganizationViewSet, DepartmentViewSet, TeamViewSet, UserViewSet,
    UserRoleViewSet, UserPermissionViewSet
)
from apps.incidents.viewsets import (
    IncidentViewSet, IncidentCommentViewSet, IncidentWorkaroundViewSet, IncidentAttachmentViewSet
)
from apps.service_requests.viewsets import (
    ServiceCategoryViewSet, ServiceViewSet, ServiceRequestViewSet,
    ServiceRequestItemViewSet, ServiceRequestApprovalViewSet, ServiceRequestAttachmentViewSet
)
from apps.problems.viewsets import ProblemViewSet, RCAViewSet, KEDBViewSet
from apps.changes.viewsets import (
    ChangeViewSet, CABMemberViewSet, ChangeApprovalViewSet,
    ChangeImpactAnalysisViewSet, ChangeLogViewSet
)
from apps.cmdb.viewsets import (
    CICategoryViewSet, CIViewSet, CIAttributeViewSet,
    CIAttributeValueViewSet, CIRelationshipViewSet
)
from apps.sla.viewsets import (
    SLAPolicyViewSet, SLATargetViewSet, SLABreachViewSet,
    SLAEscalationViewSet, SLAMetricViewSet
)
from apps.workflows.viewsets import (
    WorkflowViewSet, WorkflowStateViewSet, WorkflowTransitionViewSet, WorkflowExecutionViewSet
)
from apps.notifications.viewsets import (
    NotificationViewSet, NotificationTemplateViewSet,
    NotificationChannelViewSet, NotificationLogViewSet
)
from apps.reports.viewsets import (
    ReportViewSet, ReportScheduleViewSet, ReportExecutionViewSet,
    DashboardViewSet, DashboardWidgetViewSet
)
from apps.surveys.viewsets import (
    SurveyViewSet, SurveyQuestionViewSet, SurveyResponseViewSet, FeedbackViewSet
)
from apps.audit_logs.viewsets import AuditLogViewSet, ComplianceLogViewSet
from apps.assets.viewsets import (
    AssetCategoryViewSet, AssetViewSet, AssetDepreciationViewSet,
    AssetMaintenanceViewSet, AssetTransferViewSet
)

# Create router
router = DefaultRouter()

# Core app routes
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'users', UserViewSet, basename='user')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'user-permissions', UserPermissionViewSet, basename='user-permission')

# Incidents app routes
router.register(r'incidents', IncidentViewSet, basename='incident')
router.register(r'incident-comments', IncidentCommentViewSet, basename='incident-comment')
router.register(r'incident-workarounds', IncidentWorkaroundViewSet, basename='incident-workaround')
router.register(r'incident-attachments', IncidentAttachmentViewSet, basename='incident-attachment')

# Service Requests app routes
router.register(r'service-categories', ServiceCategoryViewSet, basename='service-category')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'service-requests', ServiceRequestViewSet, basename='service-request')
router.register(r'service-request-items', ServiceRequestItemViewSet, basename='service-request-item')
router.register(r'service-request-approvals', ServiceRequestApprovalViewSet, basename='service-request-approval')
router.register(r'service-request-attachments', ServiceRequestAttachmentViewSet, basename='service-request-attachment')

# Problems app routes
router.register(r'problems', ProblemViewSet, basename='problem')
router.register(r'root-cause-analysis', RCAViewSet, basename='rca')
router.register(r'kedb', KEDBViewSet, basename='kedb')

# Changes app routes
router.register(r'changes', ChangeViewSet, basename='change')
router.register(r'cab-members', CABMemberViewSet, basename='cab-member')
router.register(r'change-approvals', ChangeApprovalViewSet, basename='change-approval')
router.register(r'change-impact-analysis', ChangeImpactAnalysisViewSet, basename='change-impact-analysis')
router.register(r'change-logs', ChangeLogViewSet, basename='change-log')

# CMDB app routes
router.register(r'ci-categories', CICategoryViewSet, basename='ci-category')
router.register(r'configuration-items', CIViewSet, basename='configuration-item')
router.register(r'ci-attributes', CIAttributeViewSet, basename='ci-attribute')
router.register(r'ci-attribute-values', CIAttributeValueViewSet, basename='ci-attribute-value')
router.register(r'ci-relationships', CIRelationshipViewSet, basename='ci-relationship')

# SLA app routes
router.register(r'sla-policies', SLAPolicyViewSet, basename='sla-policy')
router.register(r'sla-targets', SLATargetViewSet, basename='sla-target')
router.register(r'sla-breaches', SLABreachViewSet, basename='sla-breach')
router.register(r'sla-escalations', SLAEscalationViewSet, basename='sla-escalation')
router.register(r'sla-metrics', SLAMetricViewSet, basename='sla-metric')

# Workflows app routes
router.register(r'workflows', WorkflowViewSet, basename='workflow')
router.register(r'workflow-states', WorkflowStateViewSet, basename='workflow-state')
router.register(r'workflow-transitions', WorkflowTransitionViewSet, basename='workflow-transition')
router.register(r'workflow-executions', WorkflowExecutionViewSet, basename='workflow-execution')

# Notifications app routes
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notification-templates', NotificationTemplateViewSet, basename='notification-template')
router.register(r'notification-channels', NotificationChannelViewSet, basename='notification-channel')
router.register(r'notification-logs', NotificationLogViewSet, basename='notification-log')

# Reports app routes
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'report-schedules', ReportScheduleViewSet, basename='report-schedule')
router.register(r'report-executions', ReportExecutionViewSet, basename='report-execution')
router.register(r'dashboards', DashboardViewSet, basename='dashboard')
router.register(r'dashboard-widgets', DashboardWidgetViewSet, basename='dashboard-widget')

# Surveys app routes
router.register(r'surveys', SurveyViewSet, basename='survey')
router.register(r'survey-questions', SurveyQuestionViewSet, basename='survey-question')
router.register(r'survey-responses', SurveyResponseViewSet, basename='survey-response')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

# Audit Logs app routes
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'compliance-logs', ComplianceLogViewSet, basename='compliance-log')

# Assets app routes
router.register(r'asset-categories', AssetCategoryViewSet, basename='asset-category')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'asset-depreciation', AssetDepreciationViewSet, basename='asset-depreciation')
router.register(r'asset-maintenance', AssetMaintenanceViewSet, basename='asset-maintenance')
router.register(r'asset-transfers', AssetTransferViewSet, basename='asset-transfer')


@api_view(['GET'])
def api_root(request):
    """API root endpoint with documentation"""
    return Response({
        'message': 'ITSM Platform REST API v1',
        'version': '1.0',
        'endpoints': {
            'core': {
                'organizations': request.build_absolute_uri('/api/v1/organizations/'),
                'users': request.build_absolute_uri('/api/v1/users/'),
                'teams': request.build_absolute_uri('/api/v1/teams/'),
            },
            'incident_management': {
                'incidents': request.build_absolute_uri('/api/v1/incidents/'),
                'incident_comments': request.build_absolute_uri('/api/v1/incident-comments/'),
            },
            'service_requests': {
                'requests': request.build_absolute_uri('/api/v1/service-requests/'),
                'services': request.build_absolute_uri('/api/v1/services/'),
            },
            'problem_management': {
                'problems': request.build_absolute_uri('/api/v1/problems/'),
                'root_cause_analysis': request.build_absolute_uri('/api/v1/root-cause-analysis/'),
            },
            'change_management': {
                'changes': request.build_absolute_uri('/api/v1/changes/'),
                'cab_members': request.build_absolute_uri('/api/v1/cab-members/'),
            },
            'cmdb': {
                'configuration_items': request.build_absolute_uri('/api/v1/configuration-items/'),
                'ci_relationships': request.build_absolute_uri('/api/v1/ci-relationships/'),
            },
            'sla': {
                'policies': request.build_absolute_uri('/api/v1/sla-policies/'),
                'breaches': request.build_absolute_uri('/api/v1/sla-breaches/'),
            },
            'admin': {
                'audit_logs': request.build_absolute_uri('/api/v1/audit-logs/'),
                'compliance_logs': request.build_absolute_uri('/api/v1/compliance-logs/'),
            },
        },
        'authentication': {
            'login': request.build_absolute_uri('/api/v1/auth/login/'),
            'refresh': request.build_absolute_uri('/api/v1/auth/refresh/'),
            'logout': request.build_absolute_uri('/api/v1/auth/logout/'),
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
]
