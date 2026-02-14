"""
Service Request ViewSets - REST API viewsets for service request management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Q
from django.utils import timezone
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
    ServiceRequestAttachmentSerializer, ServiceCreateUpdateSerializer
)
from apps.organizations.models import Organization, ModuleCategory
from apps.users.models import User
from apps.core.permissions import permission_required
from apps.workflows.utils import (
    ensure_workflow_instance_for_service_request,
    advance_workflow,
)


def _resolve_core_organization(user):
    user_org = getattr(user, 'organization', None)
    if user_org:
        matched = Organization.objects.filter(name=user_org.name).first()
        if matched:
            return matched
    if user.is_superuser:
        return Organization.objects.filter(is_active=True).first()
    return None


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for service categories"""
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization']
    search_fields = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
            'create': 'categories.manage',
            'update': 'categories.manage',
            'partial_update': 'categories.manage',
            'destroy': 'categories.manage',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return ServiceCategory.objects.filter(is_active=True)
        return ServiceCategory.objects.filter(organization_id=user.organization_id, is_active=True)

    def perform_create(self, serializer):
        """Set organization when creating a service category"""
        organization = _resolve_core_organization(self.request.user)
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})
        serializer.save(organization=organization)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for services"""
    queryset = Service.objects.filter(is_active=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'organization']
    search_fields = ['name', 'description']
    ordering = ['name']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
            'create': 'categories.manage',
            'update': 'categories.manage',
            'partial_update': 'categories.manage',
            'destroy': 'categories.manage',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ServiceListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceCreateUpdateSerializer
        return ServiceDetailSerializer
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Service.objects.filter(is_active=True)
        return Service.objects.filter(organization_id=user.organization_id, is_active=True)

    def perform_create(self, serializer):
        """Set organization when creating a service"""
        organization = _resolve_core_organization(self.request.user)
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})
        serializer.save(organization=organization)


class ServiceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for service requests"""
    queryset = ServiceRequest.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'requester', 'assigned_to', 'service', 'service__category']
    search_fields = ['ticket_number', 'title']
    ordering_fields = ['created_at', 'sla_due_date']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
            'create': 'service_requests.create',
            'update': 'service_requests.update',
            'partial_update': 'service_requests.update',
            'destroy': 'service_requests.update',
            'submit': 'service_requests.submit',
            'approve': 'service_requests.approve',
            'reject': 'service_requests.reject',
            'complete': 'service_requests.fulfill',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
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
        queryset = ServiceRequest.objects.filter(deleted_at__isnull=True)

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(organization_id=user.organization_id)

        if user.role == 'end_user':
            return queryset.filter(Q(requester=user) | Q(created_by=user))

        return queryset

    def get_object(self):
        service_request = super().get_object()
        user = self.request.user

        if not user.is_superuser and user.role == 'end_user':
            if service_request.requester_id != user.id and service_request.created_by_id != user.id:
                raise PermissionDenied('End users can only access their own service requests.')

        return service_request

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            for item in page:
                if item.update_breach_status():
                    item.save(update_fields=['sla_breach'])
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        for item in queryset:
            if item.update_breach_status():
                item.save(update_fields=['sla_breach'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        service_request = self.get_object()
        if service_request.update_breach_status():
            service_request.save(update_fields=['sla_breach'])
        serializer = self.get_serializer(service_request)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """Set organization and created_by"""
        organization = self._resolve_organization()
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})

        requester = serializer.validated_data.get('requester') or self.request.user
        service_request = serializer.save(
            organization=organization,
            requester=requester,
            created_by=self.request.user
        )
        ensure_workflow_instance_for_service_request(service_request, user=self.request.user)

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

    def _is_device_request(self, service_request):
        service = service_request.service
        category_name = ''
        if service and service.category:
            category_name = service.category.name or ''
        category_name = category_name.strip().lower()
        if category_name in {'hardware', 'device', 'devices', 'perangkat', 'asset', 'assets'}:
            return True

        if not service_request.organization_id:
            return False

        module_category = ModuleCategory.objects.filter(
            organization_id=service_request.organization_id,
            module='service_requests',
            name__iexact=category_name
        ).first()
        if not module_category:
            return False

        category_text = f"{module_category.name} {module_category.description}".lower()
        return any(keyword in category_text for keyword in ['hardware', 'device', 'devices', 'perangkat', 'asset'])

    def _required_approval_levels(self, service_request):
        levels = [{'level': 1, 'role': 'manager'}]
        if self._is_device_request(service_request):
            levels.append({'level': 2, 'role': 'asset_manager'})
        return levels
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a service request"""
        service_request = self.get_object()
        if service_request.status not in ['draft', 'rejected']:
            return Response(
                {'detail': 'Only draft or rejected requests can be submitted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        service_request.submitted_at = timezone.now()

        managers = User.objects.filter(
            organization_id=service_request.organization_id,
            role='manager',
            is_active=True
        )
        if not managers.exists() and not request.user.is_superuser:
            raise ValidationError({'approvals': 'No manager available for approval.'})

        if self._is_device_request(service_request):
            asset_managers = User.objects.filter(
                organization_id=service_request.organization_id,
                role='asset_manager',
                is_active=True
            )
            if not asset_managers.exists() and not request.user.is_superuser:
                raise ValidationError({'approvals': 'No asset manager available for approval.'})

        service_request.status = 'pending_approval'
        for approval in self._required_approval_levels(service_request):
            ServiceRequestApproval.objects.get_or_create(
                request=service_request,
                approval_level=approval['level'],
                defaults={
                    'approval_group': service_request.service.approval_group if service_request.service else None,
                    'status': 'pending',
                }
            )

        service_request.save(update_fields=['status', 'submitted_at'])

        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status=service_request.status, user=request.user)
        return Response({'detail': f'Request {service_request.ticket_number} submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a service request"""
        service_request = self.get_object()
        comments = request.data.get('comments', '')

        if service_request.status not in ['pending_approval', 'submitted']:
            return Response(
                {'detail': 'Request is not awaiting approval.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending = ServiceRequestApproval.objects.filter(
            request=service_request,
            status='pending'
        ).order_by('approval_level')

        if not pending.exists():
            return Response({'detail': 'No pending approvals.'}, status=status.HTTP_400_BAD_REQUEST)

        current_approval = pending.first()
        required_role = 'manager' if current_approval.approval_level == 1 else 'asset_manager'
        if not request.user.is_superuser and request.user.role != required_role:
            return Response({'detail': f'Requires {required_role} approval.'}, status=status.HTTP_403_FORBIDDEN)

        current_approval.approver = request.user
        current_approval.status = 'approved'
        current_approval.notes = comments
        current_approval.decided_at = timezone.now()
        current_approval.save(update_fields=['approver', 'status', 'notes', 'decided_at'])

        if ServiceRequestApproval.objects.filter(request=service_request, status='pending').exists():
            service_request.status = 'pending_approval'
            service_request.save(update_fields=['status'])
        else:
            service_request.status = 'approved'
            service_request.approved_at = timezone.now()
            service_request.save(update_fields=['status', 'approved_at'])

        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status='approved', user=request.user, notes=comments)
        return Response({'detail': f'Request {service_request.ticket_number} approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a service request"""
        service_request = self.get_object()
        comments = request.data.get('comments', '')

        if service_request.status not in ['pending_approval', 'submitted']:
            return Response(
                {'detail': 'Request is not awaiting approval.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        pending = ServiceRequestApproval.objects.filter(
            request=service_request,
            status='pending'
        ).order_by('approval_level')

        if not pending.exists():
            return Response({'detail': 'No pending approvals.'}, status=status.HTTP_400_BAD_REQUEST)

        current_approval = pending.first()
        required_role = 'manager' if current_approval.approval_level == 1 else 'asset_manager'
        if not request.user.is_superuser and request.user.role != required_role:
            return Response({'detail': f'Requires {required_role} approval.'}, status=status.HTTP_403_FORBIDDEN)

        current_approval.approver = request.user
        current_approval.status = 'rejected'
        current_approval.notes = comments
        current_approval.decided_at = timezone.now()
        current_approval.save(update_fields=['approver', 'status', 'notes', 'decided_at'])

        service_request.status = 'rejected'
        service_request.save(update_fields=['status'])

        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status='rejected', user=request.user, notes=comments)
        return Response({'detail': f'Request {service_request.ticket_number} rejected'})
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a service request"""
        service_request = self.get_object()
        if service_request.status not in ['approved', 'in_progress', 'pending_fulfillment']:
            return Response(
                {'detail': 'Request must be approved before fulfillment.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        service_request.status = 'fulfilled'
        service_request.fulfilled_at = timezone.now()
        service_request.save(update_fields=['status', 'fulfilled_at'])
        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status='fulfilled', user=request.user, complete=True)
        return Response({'detail': f'Request {service_request.ticket_number} fulfilled'})


class ServiceRequestItemViewSet(viewsets.ModelViewSet):
    """ViewSet for service request items"""
    queryset = ServiceRequestItem.objects.all()
    serializer_class = ServiceRequestItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['request']
    ordering = ['id']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
            'create': 'service_requests.update',
            'update': 'service_requests.update',
            'partial_update': 'service_requests.update',
            'destroy': 'service_requests.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class ServiceRequestApprovalViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing service request approvals"""
    queryset = ServiceRequestApproval.objects.all()
    serializer_class = ServiceRequestApprovalSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['request', 'approver', 'status']
    ordering = ['approval_level']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class ServiceRequestAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for service request attachments"""
    queryset = ServiceRequestAttachment.objects.all()
    serializer_class = ServiceRequestAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['request']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'service_requests.view',
            'retrieve': 'service_requests.view',
            'create': 'service_requests.update',
            'update': 'service_requests.update',
            'partial_update': 'service_requests.update',
            'destroy': 'service_requests.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
