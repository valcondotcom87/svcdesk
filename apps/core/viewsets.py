"""
Core ViewSets - REST API viewsets for user and organization management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.models import Organization, Department, Team, CustomUser, UserRole, UserPermission
from apps.core.serializers import (
    OrganizationSerializer, DepartmentSerializer, TeamSerializer,
    UserListSerializer, UserDetailSerializer, UserCreateUpdateSerializer,
    UserRoleSerializer, UserPermissionSerializer
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for organization management"""
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter organizations by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(id=user.organization_id)


class DepartmentViewSet(viewsets.ModelViewSet):
    """ViewSet for department management"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization']
    search_fields = ['name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter departments by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Department.objects.all()
        return Department.objects.filter(organization_id=user.organization_id)


class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet for team management"""
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'department']
    search_fields = ['name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter teams by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Team.objects.all()
        return Team.objects.filter(organization_id=user.organization_id)
    
    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        """Add a user to the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = CustomUser.objects.get(id=user_id)
            team.members.add(user)
            return Response({'detail': f'User {user.get_full_name()} added to team'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        """Remove a user from the team"""
        team = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = CustomUser.objects.get(id=user_id)
            team.members.remove(user)
            return Response({'detail': f'User {user.get_full_name()} removed from team'})
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for user management"""
    queryset = CustomUser.objects.filter(is_deleted=False)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['organization', 'user_type', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        """Filter users by organization"""
        user = self.request.user
        if user.is_superuser:
            return CustomUser.objects.filter(is_deleted=False)
        return CustomUser.objects.filter(organization_id=user.organization_id, is_deleted=False)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user details"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not user.check_password(old_password):
            return Response({'error': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({'detail': 'Password changed successfully'})
    
    @action(detail=True, methods=['post'])
    def disable_mfa(self, request, pk=None):
        """Disable MFA for user"""
        user = self.get_object()
        user.mfa_enabled = False
        user.mfa_method = None
        user.save()
        return Response({'detail': 'MFA disabled'})
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a user"""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({'detail': 'User activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a user"""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({'detail': 'User deactivated'})


class UserRoleViewSet(viewsets.ModelViewSet):
    """ViewSet for user role assignment"""
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'role']
    ordering = ['-created_at']


class UserPermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing user permissions"""
    queryset = UserPermission.objects.all()
    serializer_class = UserPermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['module', 'action']
    search_fields = ['module']
