"""
Users Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Organization, Team, TeamMember, Role, UserRole
from .serializers import (
    UserSerializer, UserCreateSerializer, UserUpdateSerializer,
    PasswordChangeSerializer, OrganizationSerializer, TeamSerializer,
    TeamMemberSerializer, RoleSerializer, UserRoleSerializer
)

User = get_user_model()


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
    Role ViewSet
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of system roles
        """
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
