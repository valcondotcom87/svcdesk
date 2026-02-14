"""
Change ViewSets - REST API viewsets for change management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from apps.changes.models import (
    Change, CABMember, ChangeApproval, ChangeImpactAnalysis, ChangeLog
)
from apps.changes.serializers import (
    ChangeListSerializer, ChangeDetailSerializer, ChangeCreateUpdateSerializer,
    ChangeActionSerializer, CABMemberSerializer, ChangeApprovalSerializer,
    ChangeImpactAnalysisSerializer, ChangeLogSerializer
)
from apps.organizations.models import Organization
from apps.users.models import User
from apps.core.permissions import permission_required
from apps.workflows.utils import (
    ensure_workflow_instance_for_change,
    advance_workflow,
)


class ChangeViewSet(viewsets.ModelViewSet):
    """ViewSet for change management"""
    queryset = Change.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'change_type', 'impact_level', 'requester', 'implementation_owner', 'category']
    search_fields = ['ticket_number', 'title']
    ordering_fields = ['created_at', 'implementation_date', 'completed_date']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'changes.view',
            'retrieve': 'changes.view',
            'create': 'changes.create',
            'update': 'changes.update',
            'partial_update': 'changes.update',
            'destroy': 'changes.update',
            'submit': 'changes.submit',
            'approve': 'changes.approve',
            'reject': 'changes.reject',
            'implement': 'changes.implement',
            'complete': 'changes.complete',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ChangeListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ChangeCreateUpdateSerializer
        return ChangeDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        queryset = Change.objects.filter(deleted_at__isnull=True)

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(organization_id=user.organization_id)

        if user.role == 'end_user':
            return queryset.filter(Q(requester=user) | Q(created_by=user))

        return queryset

    def get_object(self):
        change = super().get_object()
        user = self.request.user

        if not user.is_superuser and user.role == 'end_user':
            if change.requester_id != user.id and change.created_by_id != user.id:
                raise PermissionDenied('End users can only access their own changes.')

        return change
    
    def perform_create(self, serializer):
        """Set organization and created_by"""
        organization = self._resolve_organization()
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})
        requester = serializer.validated_data.get('requester') or self.request.user
        change = serializer.save(organization=organization, requester=requester, created_by=self.request.user)
        ensure_workflow_instance_for_change(change, user=self.request.user)

    def _resolve_organization(self):
        user = self.request.user
        user_org = getattr(user, 'organization', None)
        if user_org:
            matched = Organization.objects.filter(name=user_org.name).first()
            if matched:
                return matched
        if user.is_superuser:
            return Organization.objects.filter(is_active=True).first()
        return None
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a change for review"""
        change = self.get_object()
        if change.status != 'draft':
            return Response(
                {'detail': 'Only draft changes can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        managers = User.objects.filter(
            organization_id=change.organization_id,
            role='manager',
            is_active=True
        )
        if not managers.exists() and not request.user.is_superuser:
            raise ValidationError({'approvals': 'No manager available for approval.'})

        change.status = 'pending_approval'
        change.save(update_fields=['status'])

        instance = ensure_workflow_instance_for_change(change, user=request.user)
        advance_workflow(instance, status='submitted', user=request.user)
        
        ChangeLog.objects.create(
            change=change,
            action='submitted',
            created_by=request.user,
            description='Change submitted for CAB review'
        )
        
        return Response({'detail': f'Change {change.ticket_number} submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a change"""
        change = self.get_object()
        comments = request.data.get('comments', '')

        if change.status != 'pending_approval':
            return Response(
                {'detail': 'Change is not awaiting approval.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser and request.user.role != 'manager':
            return Response({'detail': 'Manager approval required.'}, status=status.HTTP_403_FORBIDDEN)
        
        cab_member, _ = CABMember.objects.get_or_create(
            change=change,
            user=request.user,
            defaults={'role': 'Member', 'is_mandatory': False}
        )

        ChangeApproval.objects.update_or_create(
            change=change,
            cab_member=cab_member,
            defaults={
                'status': 'approved',
                'comments': comments,
                'decided_at': timezone.now(),
            },
        )
        
        change.status = 'approved'
        change.save(update_fields=['status'])
        
        ChangeLog.objects.create(
            change=change,
            action='approved',
            created_by=request.user,
            description=f'Change approved by {request.user.get_full_name()}'
        )
        
        instance = ensure_workflow_instance_for_change(change, user=request.user)
        advance_workflow(instance, status='approved', user=request.user, notes=comments)

        return Response({'detail': f'Change {change.ticket_number} approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a change"""
        change = self.get_object()
        comments = request.data.get('comments', '')

        if change.status != 'pending_approval':
            return Response(
                {'detail': 'Change is not awaiting approval.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not request.user.is_superuser and request.user.role != 'manager':
            return Response({'detail': 'Manager approval required.'}, status=status.HTTP_403_FORBIDDEN)
        
        cab_member, _ = CABMember.objects.get_or_create(
            change=change,
            user=request.user,
            defaults={'role': 'Member', 'is_mandatory': False}
        )

        ChangeApproval.objects.update_or_create(
            change=change,
            cab_member=cab_member,
            defaults={
                'status': 'rejected',
                'comments': comments,
                'decided_at': timezone.now(),
            },
        )
        
        change.status = 'rejected'
        change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='rejected',
            created_by=request.user,
            description=f'Change rejected by {request.user.get_full_name()}'
        )
        
        instance = ensure_workflow_instance_for_change(change, user=request.user)
        advance_workflow(instance, status='rejected', user=request.user, notes=comments)

        return Response({'detail': f'Change {change.ticket_number} rejected'})
    
    @action(detail=True, methods=['post'])
    def implement(self, request, pk=None):
        """Implement a change"""
        change = self.get_object()
        if change.status != 'approved':
            return Response(
                {'detail': 'Only approved changes can be implemented.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        change.status = 'in_progress'
        change.save()

        instance = ensure_workflow_instance_for_change(change, user=request.user)
        advance_workflow(instance, status='in_progress', user=request.user)
        
        ChangeLog.objects.create(
            change=change,
            action='implementing',
            created_by=request.user,
            description='Change implementation started'
        )
        
        return Response({'detail': f'Change {change.ticket_number} implementation started'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a change"""
        change = self.get_object()
        if change.status != 'in_progress':
            return Response(
                {'detail': 'Change must be in progress before completion.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        change.status = 'completed'
        change.completed_date = timezone.now()
        change.save()

        instance = ensure_workflow_instance_for_change(change, user=request.user)
        advance_workflow(instance, status='completed', user=request.user, complete=True)
        
        ChangeLog.objects.create(
            change=change,
            action='completed',
            created_by=request.user,
            description='Change implementation completed'
        )
        
        return Response({'detail': f'Change {change.ticket_number} completed'})


class CABMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for CAB members"""
    queryset = CABMember.objects.all()
    serializer_class = CABMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'role']
    ordering = ['id']

    def get_permissions(self):
        action_map = {
            'list': 'changes.view',
            'retrieve': 'changes.view',
            'create': 'changes.update',
            'update': 'changes.update',
            'partial_update': 'changes.update',
            'destroy': 'changes.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class ChangeApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing change approvals"""
    queryset = ChangeApproval.objects.all()
    serializer_class = ChangeApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'cab_member', 'status']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'changes.view',
            'retrieve': 'changes.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class ChangeImpactAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for change impact analysis"""
    queryset = ChangeImpactAnalysis.objects.all()
    serializer_class = ChangeImpactAnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'changes.view',
            'retrieve': 'changes.view',
            'create': 'changes.update',
            'update': 'changes.update',
            'partial_update': 'changes.update',
            'destroy': 'changes.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class ChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing change logs"""
    queryset = ChangeLog.objects.all()
    serializer_class = ChangeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'action']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'changes.view',
            'retrieve': 'changes.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
