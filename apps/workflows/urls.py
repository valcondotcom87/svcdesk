from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.workflows import views

router = DefaultRouter()
router.register(r'workflows', views.WorkflowViewSet, basename='workflow')
router.register(r'workflow-steps', views.WorkflowStepViewSet, basename='workflowstep')

urlpatterns = [
    path('', include(router.urls)),
]
