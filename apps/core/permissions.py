"""
Core Permissions - RBAC implementation
"""
from rest_framework import permissions


class IsTenantUser(permissions.BasePermission):
    """Check if user belongs to the organization"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user.organization == obj.organization


class IsAdmin(permissions.BasePermission):
    """Check if user is admin"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsTeamManager(permissions.BasePermission):
    """Check if user is team manager"""
    
    def has_permission(self, request, view):
        return request.user and hasattr(request.user, 'team_member')


class IsIncidentAgent(permissions.BasePermission):
    """Check if user can work on incidents"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.groups.filter(name='Incident Agent').exists()
