"""
Service Request ViewSets - REST API viewsets for service request management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F, Q, Value
from django.utils import timezone
from django.db.models.functions import Coalesce, TruncMonth
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
from apps.sla.utils import (
    apply_sla_dates,
    apply_sla_pause,
    resolve_sla_targets,
    select_sla_policy_for_service_request,
    _priority_to_severity,
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
                    item.save(update_fields=['sla_breach', 'sla_response_breach'])
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        for item in queryset:
            if item.update_breach_status():
                item.save(update_fields=['sla_breach', 'sla_response_breach'])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        service_request = self.get_object()
        if service_request.update_breach_status():
            service_request.save(update_fields=['sla_breach', 'sla_response_breach'])
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

    def _ensure_same_org(self, service_request, user):
        if user.is_superuser:
            return
        user_org = getattr(user, 'organization', None)
        if not user_org or user_org.name != service_request.organization.name:
            raise PermissionDenied('User must belong to the same organization.')

    def _required_approval_levels(self, service_request):
        levels = [{'level': 1, 'role': 'manager'}]
        if self._is_device_request(service_request):
            levels.append({'level': 2, 'role': 'asset_manager'})
        return levels
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit a service request"""
        service_request = self.get_object()
        self._ensure_same_org(service_request, request.user)
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

        if not service_request.sla_policy:
            policy = select_sla_policy_for_service_request(service_request)
            if policy:
                service_request.sla_policy = policy
                severity = _priority_to_severity(service_request.priority, is_incident=False)
                response_minutes, resolution_minutes = resolve_sla_targets(policy, severity)
                updated = ['sla_policy']
                updated.extend(apply_sla_dates(
                    service_request,
                    response_minutes,
                    resolution_minutes,
                    service_request.submitted_at or service_request.created_at
                ))
                service_request.save(update_fields=sorted(set(updated)))

        pause_fields = apply_sla_pause(service_request, True)
        if pause_fields:
            service_request.save(update_fields=sorted(set(pause_fields)))

        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status=service_request.status, user=request.user)
        return Response({'detail': f'Request {service_request.ticket_number} submitted'})
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a service request"""
        service_request = self.get_object()
        self._ensure_same_org(service_request, request.user)
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
            if service_request.first_response_at is None:
                service_request.first_response_at = timezone.now()
                service_request.save(update_fields=['status', 'approved_at', 'first_response_at'])
            else:
                service_request.save(update_fields=['status', 'approved_at'])

        instance = ensure_workflow_instance_for_service_request(service_request, user=request.user)
        advance_workflow(instance, status='approved', user=request.user, notes=comments)
        return Response({'detail': f'Request {service_request.ticket_number} approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a service request"""
        service_request = self.get_object()
        self._ensure_same_org(service_request, request.user)
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
        self._ensure_same_org(service_request, request.user)
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

    @action(detail=False, methods=['get'])
    def report(self, request):
        """Service request reporting metrics for month/year and status breakdowns."""
        now = timezone.now()
        try:
            month = int(request.query_params.get('month', now.month))
            year = int(request.query_params.get('year', now.year))
        except ValueError:
            return Response({'detail': 'Invalid month or year.'}, status=status.HTTP_400_BAD_REQUEST)

        if month < 1 or month > 12:
            return Response({'detail': 'Month must be between 1 and 12.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_queryset()

        active_statuses = ['submitted', 'pending_approval', 'approved', 'in_progress', 'pending_fulfillment']
        fulfilled_statuses = ['fulfilled', 'closed']
        failed_statuses = ['rejected']

        report_queryset = queryset.exclude(status='draft')

        raised_month_count = report_queryset.filter(
            submitted_at__year=year,
            submitted_at__month=month
        ).count()
        raised_year_count = report_queryset.filter(submitted_at__year=year).count()

        active_count = report_queryset.filter(status__in=active_statuses).count()
        fulfilled_count = report_queryset.filter(status__in=fulfilled_statuses).count()
        waiting_approval_count = report_queryset.filter(status='pending_approval').count()
        failed_count = report_queryset.filter(status__in=failed_statuses).count()

        active_age_qs = report_queryset.filter(status__in=active_statuses)
        avg_age = active_age_qs.aggregate(
            avg_age=Avg(
                ExpressionWrapper(
                    now - Coalesce('submitted_at', 'created_at'),
                    output_field=DurationField()
                )
            )
        )['avg_age']
        avg_age_days = round(avg_age.total_seconds() / 86400, 2) if avg_age else 0

        category_counts = (
            report_queryset
            .annotate(category_name=Coalesce('service__category__name', Value('Uncategorized')))
            .values('category_name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        top_categories = [
            {'category': item['category_name'], 'count': item['count']}
            for item in category_counts[:10]
        ]

        status_breakdown = (
            report_queryset.values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        status_counts = {item['status']: item['count'] for item in status_breakdown}
        for status_code, _ in ServiceRequest.STATUS_CHOICES:
            status_counts.setdefault(status_code, 0)

        monthly_breakdown = (
            report_queryset.filter(submitted_at__year=year)
            .annotate(month=TruncMonth('submitted_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        monthly_counts = [
            {'month': item['month'].strftime('%Y-%m'), 'count': item['count']}
            for item in monthly_breakdown
        ]

        payload = {
            'period': {'month': month, 'year': year},
            'raised': {
                'month': raised_month_count,
                'year': raised_year_count,
            },
            'active_service_requests': active_count,
            'fulfilled_service_requests': fulfilled_count,
            'waiting_approval_service_requests': waiting_approval_count,
            'failed_service_requests': failed_count,
            'average_age_days': avg_age_days,
            'top_request_categories': top_categories,
            'service_requests_by_status': status_counts,
            'service_requests_by_month': monthly_counts,
            'fulfilled_statuses': fulfilled_statuses,
            'active_statuses': active_statuses,
            'failed_statuses': failed_statuses,
        }

        return Response(payload)


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
