"""
Users Admin
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Organization, Team, TeamMember, Role, UserRole


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Organization admin
    """
    list_display = ['name', 'domain', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'domain']
    ordering = ['name']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin
    """
    list_display = ['email', 'username', 'first_name', 'last_name', 'role', 'organization', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'organization']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Organization', {'fields': ('organization', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Security', {'fields': ('mfa_enabled', 'failed_login_attempts', 'locked_until')}),
        ('Important dates', {'fields': ('last_login', 'password_changed_at', 'created_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'organization', 'role'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """
    Team admin
    """
    list_display = ['name', 'organization', 'team_lead', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Team Member admin
    """
    list_display = ['user', 'team', 'role', 'joined_at']
    list_filter = ['role', 'team', 'joined_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'team__name']
    ordering = ['-joined_at']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Role admin
    """
    list_display = ['name', 'is_system_role', 'created_at']
    list_filter = ['is_system_role', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_system_role:
            return ['name', 'is_system_role']
        return ['is_system_role']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    User Role admin
    """
    list_display = ['user', 'role', 'assigned_by', 'assigned_at']
    list_filter = ['role', 'assigned_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'role__name']
    ordering = ['-assigned_at']
