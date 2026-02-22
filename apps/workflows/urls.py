from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.workflows import viewsets

router = DefaultRouter()
router.register(r'workflows', viewsets.WorkflowViewSet, basename='workflow')
router.register(r'workflow-steps', viewsets.WorkflowStepViewSet, basename='workflowstep')
router.register(r'workflow-instances', viewsets.WorkflowInstanceViewSet, basename='workflowinstance')
router.register(r'workflow-transitions', viewsets.WorkflowTransitionViewSet, basename='workflowtransition')

urlpatterns = [
    path('', include(router.urls)),
]
