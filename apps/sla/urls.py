from django.urls import include, path
from rest_framework.routers import DefaultRouter
from apps.sla import viewsets

router = DefaultRouter()
router.register(r'slas', viewsets.SLAPolicyViewSet, basename='sla')
router.register(r'sla-targets', viewsets.SLATargetViewSet, basename='slatarget')
router.register(r'sla-breaches', viewsets.SLABreachViewSet, basename='slabreach')
router.register(r'sla-escalations', viewsets.SLAEscalationViewSet, basename='slaescalation')
router.register(r'sla-metrics', viewsets.SLAMetricViewSet, basename='slametric')

urlpatterns = [
    path('', include(router.urls)),
]
