"""
Users URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet, OrganizationViewSet,
    TeamViewSet, RoleViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    # Include router URLs (users, teams, organizations, roles)
    path('', include(router.urls)),
]
