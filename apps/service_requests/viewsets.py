"""
Service Request ViewSets - REST API viewsets for service request management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.service_requests.models import (
    ServiceCategory, Service, ServiceRequest, ServiceRequestApproval,
    ServiceRequestItem, ServiceRequestAttachment
)
from apps.service_requests.serializers import (
    ServiceCategorySerializer, ServiceListSerializer, ServiceDetailSerializer,
    ServiceRequestListSerializer, ServiceRequestDetailSerializer,
    ServiceRequestCreateUpdateSerializer, ServiceRequestActionSerializer,
    ServiceRequestItemSerializer, ServiceRequestApprovalSerializer,
    ServiceRequestAttachmentSerializer
)


class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for service categories"""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization']
    search_fields = ['name']
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ServiceCategory.objects.filter(is_active=True)
        return ServiceCategory.objects.filter(organization_id=user.organization_id, is_active=True)


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for services"""
    queryset = Service.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'organization']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ServiceListSerializer
        return ServiceDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Service.objects.filter(is_active=True)
        return Service.objects.filter(organization_id=user.organization_id, is_active=True)


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for service requests"""
    queryset = ServiceRequest.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'requester', 'assigned_to']
    search_fields = ['request_number', 'title']
    ordering_fields = ['created_at', 'sla_due_date']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ServiceRequestListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ServiceRequestCreateUpdateSerializer
        return ServiceRequestDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ServiceRequest.objects.filter(deleted_at__isnull=True)
        return ServiceRequest.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)
    
    def perform_create(self, serializer):
        """Set organization and created_by"""
        serializer.save(organization=self.request.user.organization, created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a service request"""
        service_request = self.get_object()
        service_request.status = 'submitted'
        service_request.save()
        return Response({'detail': f'Request {service_request.request_number} submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a service request"""
        service_request = self.get_object()
        comments = request.data.get('comments', '')
        
        ServiceRequestApproval.objects.create(
            service_request=service_request,
            approver=request.user,
            status='approved',
            comments=comments
        )
        
        service_request.status = 'approved'
        service_request.save()
        return Response({'detail': f'Request {service_request.request_number} approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a service request"""
        service_request = self.get_object()
        comments = request.data.get('comments', '')
        
        ServiceRequestApproval.objects.create(
            service_request=service_request,
            approver=request.user,
            status='rejected',
            comments=comments
        )
        
        service_request.status = 'rejected'
        service_request.save()
        return Response({'detail': f'Request {service_request.request_number} rejected'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a service request"""
        service_request = self.get_object()
        service_request.status = 'completed'
        service_request.actual_completion_date = timezone.now()
        service_request.save()
        return Response({'detail': f'Request {service_request.request_number} completed'})


class ServiceRequestItemViewSet(viewsets.ModelViewSet):
    """ViewSet for service request items"""
    queryset = ServiceRequestItem.objects.all()
    serializer_class = ServiceRequestItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service_request', 'service']
    ordering = ['id']


class ServiceRequestApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing service request approvals"""
    queryset = ServiceRequestApproval.objects.all()
    serializer_class = ServiceRequestApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service_request', 'approver', 'status']
    ordering = ['approval_order']


class ServiceRequestAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for service request attachments"""
    queryset = ServiceRequestAttachment.objects.all()
    serializer_class = ServiceRequestAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service_request']
    ordering = ['-created_at']
