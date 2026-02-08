from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplianceFrameworkViewSet, ComplianceRequirementViewSet,
    ImmutableAuditLogViewSet, IncidentResponsePlanViewSet,
    VulnerabilityTrackingViewSet, ComplianceCheckpointViewSet
)

app_name = 'compliance'

router = DefaultRouter()
router.register(r'frameworks', ComplianceFrameworkViewSet, basename='framework')
router.register(r'requirements', ComplianceRequirementViewSet, basename='requirement')
router.register(r'audit-logs', ImmutableAuditLogViewSet, basename='audit-log')
router.register(r'incident-plans', IncidentResponsePlanViewSet, basename='incident-plan')
router.register(r'vulnerabilities', VulnerabilityTrackingViewSet, basename='vulnerability')
router.register(r'checkpoints', ComplianceCheckpointViewSet, basename='checkpoint')

urlpatterns = [
    path('', include(router.urls)),
]
