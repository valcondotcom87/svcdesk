"""
Users URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, OrganizationViewSet,
    TeamViewSet, RoleViewSet, UserRoleViewSet,
    ADSyncLogViewSet, ADConfigurationViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'user-organizations', OrganizationViewSet, basename='user-organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'ad-sync-logs', ADSyncLogViewSet, basename='ad-sync-log')
router.register(r'ad-configuration', ADConfigurationViewSet, basename='ad-configuration')

urlpatterns = [
    # Include router URLs (users, teams, organizations, roles)
    path('', include(router.urls)),
]
