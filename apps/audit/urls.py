from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.audit import views

router = DefaultRouter()
router.register(r'audit-logs', views.AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('', include(router.urls)),
]
