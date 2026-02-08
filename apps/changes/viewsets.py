"""
Change ViewSets - REST API viewsets for change management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.changes.models import (
    Change, CABMember, ChangeApproval, ChangeImpactAnalysis, ChangeLog
)
from apps.changes.serializers import (
    ChangeListSerializer, ChangeDetailSerializer, ChangeCreateUpdateSerializer,
    ChangeActionSerializer, CABMemberSerializer, ChangeApprovalSerializer,
    ChangeImpactAnalysisSerializer, ChangeLogSerializer
)


class ChangeViewSet(viewsets.ModelViewSet):
    """ViewSet for change management"""
    queryset = Change.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'change_type', 'priority', 'assigned_to']
    search_fields = ['change_number', 'title']
    ordering_fields = ['created_at', 'scheduled_start']
    ordering = ['-created_at']
    
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
        if user.is_superuser:
            return Change.objects.filter(deleted_at__isnull=True)
        return Change.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)
    
    def perform_create(self, serializer):
        """Set organization and created_by"""
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a change for review"""
        change = self.get_object()
        change.status = 'submitted'
        change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='submitted',
            user=request.user,
            description='Change submitted for CAB review'
        )
        
        return Response({'detail': f'Change {change.change_number} submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a change"""
        change = self.get_object()
        comments = request.data.get('comments', '')
        
        approval = ChangeApproval.objects.create(
            change=change,
            approver=request.user,
            status='approved',
            comments=comments
        )
        
        # Check if all approvals are done
        pending = ChangeApproval.objects.filter(change=change, status='pending').count()
        if pending == 0:
            change.status = 'approved'
            change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='approved',
            user=request.user,
            description=f'Change approved by {request.user.get_full_name()}'
        )
        
        return Response({'detail': f'Change {change.change_number} approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a change"""
        change = self.get_object()
        comments = request.data.get('comments', '')
        
        ChangeApproval.objects.create(
            change=change,
            approver=request.user,
            status='rejected',
            comments=comments
        )
        
        change.status = 'rejected'
        change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='rejected',
            user=request.user,
            description=f'Change rejected by {request.user.get_full_name()}'
        )
        
        return Response({'detail': f'Change {change.change_number} rejected'})
    
    @action(detail=True, methods=['post'])
    def implement(self, request, pk=None):
        """Implement a change"""
        change = self.get_object()
        change.status = 'implementing'
        change.actual_start = timezone.now()
        change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='implementing',
            user=request.user,
            description='Change implementation started'
        )
        
        return Response({'detail': f'Change {change.change_number} implementation started'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a change"""
        change = self.get_object()
        change.status = 'completed'
        change.actual_end = timezone.now()
        change.save()
        
        ChangeLog.objects.create(
            change=change,
            action='completed',
            user=request.user,
            description='Change implementation completed'
        )
        
        return Response({'detail': f'Change {change.change_number} completed'})


class CABMemberViewSet(viewsets.ModelViewSet):
    """ViewSet for CAB members"""
    queryset = CABMember.objects.all()
    serializer_class = CABMemberSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'role']
    ordering = ['id']


class ChangeApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing change approvals"""
    queryset = ChangeApproval.objects.all()
    serializer_class = ChangeApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'approver', 'status']
    ordering = ['approval_order']


class ChangeImpactAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for change impact analysis"""
    queryset = ChangeImpactAnalysis.objects.all()
    serializer_class = ChangeImpactAnalysisSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'risk_level']
    ordering = ['-analysis_date']


class ChangeLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing change logs"""
    queryset = ChangeLog.objects.all()
    serializer_class = ChangeLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['change', 'action']
    ordering = ['-timestamp']
