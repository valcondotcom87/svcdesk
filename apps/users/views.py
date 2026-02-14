"""
Users Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from django_filters.rest_framework import DjangoFilterBackend

from .models import Organization, Team, TeamMember, Role, UserRole, ADSyncLog
from apps.organizations.models import Organization as CoreOrganization
from .ad_config import ADConfiguration
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, OrganizationSerializer, TeamSerializer,
    TeamMemberSerializer, RoleSerializer, UserRoleSerializer,
    ADSyncLogSerializer
)
from .ad_config_serializers import ADConfigurationSerializer

User = get_user_model()

ROLE_PERMISSION_MAP = {
    'admin': [
        'users.manage',
        'organizations.manage',
        'ad.sync',
        'users.impersonate',
        'categories.manage',
    ],
    'manager': ['users.manage', 'categories.manage'],
    'asset_manager': [],
    'engineer': [],
    'agent': [],
    'end_user': [],
}


def get_user_permissions(user):
    if user.is_superuser or user.is_staff:
        return {'*'}
    permissions = set(ROLE_PERMISSION_MAP.get(user.role, []))
    for user_role in UserRole.objects.filter(user=user).select_related('role'):
        permissions.update(user_role.role.permissions or [])
    return permissions


def require_permission(user, permission):
    if user.is_superuser or user.is_staff:
        return
    if permission in get_user_permissions(user) or '*' in get_user_permissions(user):
        return
    raise PermissionDenied(f'Permission required: {permission}')


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with additional user data
    """
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = User.objects.get(email=request.data.get('email'))
            
            # Check if account is locked
            if user.is_locked():
                return Response({
                    'success': False,
                    'error': {
                        'code': 'ACCOUNT_LOCKED',
                        'message': 'Account is temporarily locked. Please try again later.'
                    }
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = timezone.now()
            user.save(update_fields=['failed_login_attempts', 'last_login'])
            
            # Add user data to response
            response.data['user'] = UserSerializer(user).data
            response.data['success'] = True
        
        return response


class UserViewSet(viewsets.ModelViewSet):
    """
    User ViewSet
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Filter users by organization if not admin
        """
        user = self.request.user
        queryset = User.objects.all()
        
        if not user.is_superuser and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        # Filter by query params
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.select_related('organization')
    
    def create(self, request, *args, **kwargs):
        """
        Create new user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'data': UserSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update user
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'data': UserSerializer(user).data,
            'message': 'User updated successfully'
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete user (deactivate)
        """
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        
        return Response({
            'success': True,
            'message': 'User deactivated successfully'
        }, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user profile
        """
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password
        """
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.password_changed_at = timezone.now()
        user.save(update_fields=['password', 'password_changed_at'])
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })

    @action(detail=True, methods=['post'])
    def impersonate(self, request, pk=None):
        """Impersonate a user and return tokens"""
        require_permission(request.user, 'users.impersonate')

        target_user = self.get_object()
        if not target_user.is_active:
            return Response({
                'success': False,
                'error': {
                    'code': 'USER_INACTIVE',
                    'message': 'Target user is inactive'
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(target_user)

        return Response({
            'success': True,
            'impersonator': UserSerializer(request.user).data,
            'user': UserSerializer(target_user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })

    @action(detail=False, methods=['post'])
    def ad_sync(self, request):
        """Trigger AD/LDAP sync for users"""
        require_permission(request.user, 'ad.sync')
        from .ad_sync import sync_ldap_users

        result = sync_ldap_users(triggered_by_id=request.user.id, source='manual')
        status_code = status.HTTP_200_OK if result.get('success') else status.HTTP_400_BAD_REQUEST
        return Response(result, status=status_code)
    
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """
        Admin reset user password
        """
        if not request.user.role in ['admin', 'manager']:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'You do not have permission to reset passwords'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'New password is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.password_changed_at = timezone.now()
        user.save(update_fields=['password', 'password_changed_at'])
        
        return Response({
            'success': True,
            'message': 'Password reset successfully'
        })


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization ViewSet
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter organizations
        """
        user = self.request.user
        queryset = Organization.objects.all()
        
        # Non-admin users can only see their own organization
        if not user.is_superuser and user.organization:
            queryset = queryset.filter(id=user.organization.id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        require_permission(request.user, 'organizations.manage')
        response = super().create(request, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            org_id = response.data.get('id')
            if org_id:
                org = Organization.objects.filter(id=org_id).first()
                if org:
                    self._sync_core_org(org)
        return response

    def update(self, request, *args, **kwargs):
        require_permission(request.user, 'organizations.manage')
        response = super().update(request, *args, **kwargs)
        if response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            org_id = response.data.get('id')
            if org_id:
                org = Organization.objects.filter(id=org_id).first()
                if org:
                    self._sync_core_org(org)
        return response

    def destroy(self, request, *args, **kwargs):
        require_permission(request.user, 'organizations.manage')
        return super().destroy(request, *args, **kwargs)

    def _sync_core_org(self, org):
        slug = slugify(org.name) or slugify(org.domain or 'org')
        email = f"admin@{org.domain}" if org.domain else f"admin@{slug}.local"

        core_org, created = CoreOrganization.objects.get_or_create(
            name=org.name,
            defaults={
                'slug': slug,
                'email': email,
                'description': '',
                'is_active': org.is_active,
            }
        )
        if not created:
            updates = {
                'slug': slug,
                'email': core_org.email or email,
                'is_active': org.is_active,
            }
            CoreOrganization.objects.filter(id=core_org.id).update(**updates)


class TeamViewSet(viewsets.ModelViewSet):
    """
    Team ViewSet
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter teams by organization
        """
        user = self.request.user
        queryset = Team.objects.all()
        
        if not user.is_superuser and user.organization:
            queryset = queryset.filter(organization=user.organization)
        
        return queryset.select_related('organization', 'team_lead')

    def perform_create(self, serializer):
        """Set organization when creating a team"""
        if self.request.user.organization:
            serializer.save(organization=self.request.user.organization)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """
        Add member to team
        """
        team = self.get_object()
        user_id = request.data.get('user_id')
        role = request.data.get('role', 'member')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'user_id is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already a member
        if TeamMember.objects.filter(team=team, user=user).exists():
            return Response({
                'success': False,
                'error': {
                    'code': 'ALREADY_MEMBER',
                    'message': 'User is already a member of this team'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        member = TeamMember.objects.create(
            team=team,
            user=user,
            role=role
        )
        
        return Response({
            'success': True,
            'data': TeamMemberSerializer(member).data,
            'message': 'Member added successfully'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_member(self, request, pk=None):
        """
        Remove member from team
        """
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'user_id is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            member = TeamMember.objects.get(team=team, user_id=user_id)
            member.delete()
            
            return Response({
                'success': True,
                'message': 'Member removed successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except TeamMember.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'MEMBER_NOT_FOUND',
                    'message': 'Member not found in this team'
                }
            }, status=status.HTTP_404_NOT_FOUND)


class RoleViewSet(viewsets.ModelViewSet):
    """
    Role ViewSet with RBAC management
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter roles - non-admin users see only assigned roles"""
        user = self.request.user
        queryset = Role.objects.all()
        
        # Non-admin users see only roles they're assigned to
        if not user.is_superuser and not user.is_staff:
            queryset = queryset.filter(role_users__user=user).distinct()
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Admin only: Create new role with permissions"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can create roles'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Admin only: Update role and permissions"""
        instance = self.get_object()
        
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can update roles'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        if instance.is_system_role:
            return Response({
                'success': False,
                'error': {
                    'code': 'CANNOT_MODIFY_SYSTEM_ROLE',
                    'message': 'System roles cannot be modified'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Admin only: Delete role (system roles cannot be deleted)"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can delete roles'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        
        if instance.is_system_role:
            return Response({
                'success': False,
                'error': {
                    'code': 'CANNOT_DELETE_SYSTEM_ROLE',
                    'message': 'System roles cannot be deleted'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['post'])
    def assign_user(self, request, pk=None):
        """Assign role to a user"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can assign roles'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'user_id is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': 'User not found'
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create or update user role
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user}
        )
        
        return Response({
            'success': True,
            'data': UserRoleSerializer(user_role).data,
            'message': 'Role assigned successfully'
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['delete'])
    def unassign_user(self, request, pk=None):
        """Unassign role from a user"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can unassign roles'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        user_id = request.data.get('user_id')
        
        if not user_id:
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'user_id is required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_role = UserRole.objects.get(user_id=user_id, role=role)
            user_role.delete()
            
            return Response({
                'success': True,
                'message': 'Role unassigned successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except UserRole.DoesNotExist:
            return Response({
                'success': False,
                'error': {
                    'code': 'USER_ROLE_NOT_FOUND',
                    'message': 'User role assignment not found'
                }
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def update_permissions(self, request, pk=None):
        """Update role permissions"""
        if not request.user.is_staff and not request.user.is_superuser:
            return Response({
                'success': False,
                'error': {
                    'code': 'INSUFFICIENT_PERMISSIONS',
                    'message': 'Only administrators can update permissions'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        
        if role.is_system_role:
            return Response({
                'success': False,
                'error': {
                    'code': 'CANNOT_MODIFY_SYSTEM_ROLE',
                    'message': 'System role permissions cannot be modified'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        permissions = request.data.get('permissions', [])
        
        if not isinstance(permissions, list):
            return Response({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Permissions must be a list'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        role.permissions = permissions
        role.save(update_fields=['permissions'])
        
        return Response({
            'success': True,
            'data': RoleSerializer(role).data,
            'message': 'Permissions updated successfully'
        })


class UserRoleViewSet(viewsets.ModelViewSet):
    """User role assignments"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'role']
    ordering = ['-assigned_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return UserRole.objects.all()
        return UserRole.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        require_permission(request.user, 'users.manage')
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        require_permission(request.user, 'users.manage')
        return super().destroy(request, *args, **kwargs)
    
    @action(detail=False, methods=['get'])
    def available_permissions(self, request):
        """List all available permissions for roles"""
        permissions = [
            # Incidents
            'incidents.create',
            'incidents.read',
            'incidents.update',
            'incidents.delete',
            'incidents.resolve',
            'incidents.close',
            
            # Service Requests
            'service_requests.create',
            'service_requests.read',
            'service_requests.update',
            'service_requests.delete',
            'service_requests.approve',
            'service_requests.fulfill',
            
            # Problems
            'problems.create',
            'problems.read',
            'problems.update',
            'problems.delete',
            'problems.resolve',
            
            # Changes
            'changes.create',
            'changes.read',
            'changes.update',
            'changes.delete',
            'changes.approve',
            'changes.implement',
            
            # Assets
            'assets.create',
            'assets.read',
            'assets.update',
            'assets.delete',
            'assets.assign',
            
            # CMDB
            'cmdb.create',
            'cmdb.read',
            'cmdb.update',
            'cmdb.delete',
            
            # Knowledge
            'knowledge.create',
            'knowledge.read',
            'knowledge.update',
            'knowledge.delete',
            'knowledge.publish',
            
            # SLA
            'sla.create',
            'sla.read',
            'sla.update',
            'sla.delete',
            
            # Reports
            'reports.read',
            'reports.create',
            'reports.export',
            
            # User Management
            'users.create',
            'users.read',
            'users.update',
            'users.delete',
            'users.reset_password',
            'users.manage',
            'users.impersonate',
            'organizations.manage',
            'categories.manage',
            'ad.sync',
            
            # Administrative
            'admin.roles',
            'admin.settings',
            'admin.audit_logs',
            'admin.compliance',
        ]
        
        return Response({
            'success': True,
            'data': permissions,
            'count': len(permissions)
        })


class ADSyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for AD sync history."""
    queryset = ADSyncLog.objects.all()
    serializer_class = ADSyncLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'triggered_by']
    ordering = ['-started_at']

    def get_queryset(self):
        require_permission(self.request.user, 'ad.sync')
        return ADSyncLog.objects.all()


class ADConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for AD configuration management."""
    queryset = ADConfiguration.objects.all()
    serializer_class = ADConfigurationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['organization', 'is_enabled']
    ordering = ['organization__name']

    def get_queryset(self):
        require_permission(self.request.user, 'ad.sync')
        user = self.request.user
        if user.is_superuser:
            return ADConfiguration.objects.all()
        if user.organization:
            return ADConfiguration.objects.filter(organization=user.organization)
        return ADConfiguration.objects.none()

    def perform_create(self, serializer):
        require_permission(self.request.user, 'ad.sync')
        user = self.request.user
        if user.organization:
            serializer.save(organization=user.organization)
        else:
            serializer.save()

    def perform_update(self, serializer):
        require_permission(self.request.user, 'ad.sync')
        serializer.save()

    def perform_destroy(self, instance):
        require_permission(self.request.user, 'ad.sync')
        instance.delete()

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test AD connection with provided configuration."""
        require_permission(request.user, 'ad.sync')
        
        config = self.get_object()
        
        if not config.is_configured:
            return Response(
                {'detail': 'AD configuration is incomplete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Test LDAP connection
            import ldap
            
            try:
                ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            except Exception:
                pass
            
            conn = ldap.initialize(config.connection_string)
            conn.simple_bind_s(config.bind_username, config.bind_password)
            conn.unbind_s()
            
            return Response({
                'success': True,
                'message': f'Successfully connected to {config.server_name}:{config.server_port}',
                'connection_string': config.connection_string
            })
        
        except ImportError:
            return Response(
                {'detail': 'python-ldap is not installed. Install it with: pip install python-ldap'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'detail': f'Connection failed: {str(e)}',
                    'error_type': type(e).__name__
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def sync_now(self, request, pk=None):
        """Trigger immediate AD sync."""
        require_permission(request.user, 'ad.sync')
        
        config = self.get_object()
        
        if not config.is_enabled:
            return Response(
                {'detail': 'AD sync is disabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not config.is_configured:
            return Response(
                {'detail': 'AD configuration is incomplete'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Trigger AD sync task
            from apps.users.ad_sync import sync_users_from_ad
            
            result = sync_users_from_ad.delay(config.organization_id)
            
            return Response({
                'success': True,
                'message': 'AD sync started',
                'task_id': str(result.id),
                'organization': config.organization.name
            })
        
        except Exception as e:
            return Response(
                {
                    'success': False,
                    'detail': f'Failed to start sync: {str(e)}'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

