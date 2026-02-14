"""
Core Permissions - RBAC implementation
"""
from rest_framework import permissions
from functools import wraps
from rest_framework.exceptions import PermissionDenied


class IsTenantUser(permissions.BasePermission):
    """Check if user belongs to the organization"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user.organization == obj.organization


class IsAdmin(permissions.BasePermission):
    """Check if user is admin or superuser"""
    
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsManager(permissions.BasePermission):
    """Check if user is manager role"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['manager', 'admin']


class IsAgent(permissions.BasePermission):
    """Check if user is agent or above"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['agent', 'manager', 'admin']


class IsEndUser(permissions.BasePermission):
    """Check if user is authenticated (any role)"""
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsTeamManager(permissions.BasePermission):
    """Check if user is team manager/lead"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        # Check if user is team lead or manager
        from apps.users.models import TeamMember
        is_team_lead = TeamMember.objects.filter(
            user=request.user,
            role='lead'
        ).exists()
        return is_team_lead or request.user.role in ['manager', 'admin']


class HasRole(permissions.BasePermission):
    """Check if user has a specific role"""
    required_roles = []
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in self.required_roles


DEFAULT_ROLE_PERMISSION_MAP = {
    'admin': {'users.manage', 'organizations.manage', 'ad.sync', 'users.impersonate', 'categories.manage'},
    'manager': {'users.manage', 'categories.manage'},
    'agent': set(),
    'end_user': set(),
}


class HasPermission(permissions.BasePermission):
    """Check if user has a specific permission"""
    required_permission = None
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Check user object permissions
        if request.user.is_superuser or request.user.is_staff:
            return True
        
        # Check role-based permissions (role field)
        role_permissions = DEFAULT_ROLE_PERMISSION_MAP.get(request.user.role, set())
        if self.required_permission in role_permissions:
            return True

        # Check role-based permissions (UserRole assignments)
        from apps.users.models import UserRole
        user_roles = UserRole.objects.filter(user=request.user).select_related('role')
        
        for user_role in user_roles:
            if self.required_permission in user_role.role.permissions:
                return True
        
        return False


class IsIncidentAgent(permissions.BasePermission):
    """Check if user can work on incidents"""
    
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.role in ['agent', 'manager', 'admin']


# RBAC Decorators
def require_role(*roles):
    """Decorator to require specific roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied('Authentication required')
            
            if request.user.role not in roles and not request.user.is_superuser:
                raise PermissionDenied(f'Required role: {", ".join(roles)}')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_permission(permission):
    """Decorator to require specific permission"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from apps.users.models import UserRole
            
            if not request.user.is_authenticated:
                raise PermissionDenied('Authentication required')
            
            if request.user.is_superuser or request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Check role permissions
            user_roles = UserRole.objects.filter(user=request.user).select_related('role')
            has_permission = any(
                permission in role.role.permissions 
                for role in user_roles
            )
            
            if not has_permission:
                raise PermissionDenied(f'Permission required: {permission}')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
