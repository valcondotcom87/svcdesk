"""
Incident ViewSets - REST API viewsets for incident management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied
from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from apps.incidents.models import (
    Incident, IncidentComment, IncidentWorkaround, IncidentAttachment,
    IncidentPriority, IncidentStatus, IncidentCommunication
)
from apps.incidents.serializers import (
    IncidentListSerializer, IncidentDetailSerializer, IncidentCreateUpdateSerializer,
    IncidentActionSerializer, IncidentCommentSerializer, IncidentWorkaroundSerializer,
    IncidentAttachmentSerializer, IncidentCommunicationSerializer
)
from apps.organizations.models import Organization
from apps.users.models import User
from apps.core.permissions import permission_required
from apps.workflows.utils import (
    ensure_workflow_instance_for_incident,
    advance_workflow,
)


class IncidentViewSet(viewsets.ModelViewSet):
    """ViewSet for incident management"""
    queryset = Incident.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'category']
    search_fields = ['ticket_number', 'title', 'description']
    ordering_fields = ['created_at', 'priority', 'sla_due_date']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'incidents.view',
            'retrieve': 'incidents.view',
            'create': 'incidents.create',
            'update': 'incidents.update',
            'partial_update': 'incidents.update',
            'destroy': 'incidents.update',
            'resolve': 'incidents.resolve',
            'close': 'incidents.close',
            'reopen': 'incidents.reopen',
            'assign': 'incidents.assign',
            'escalate': 'incidents.escalate',
            'comments': 'incidents.view',
            'add_comment': 'incidents.comment',
            'add_communication': 'incidents.communicate',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return IncidentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncidentCreateUpdateSerializer
        return IncidentDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create incident and return detail payload including id."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail_serializer = IncidentDetailSerializer(
            serializer.instance,
            context=self.get_serializer_context(),
        )
        headers = self.get_success_headers(detail_serializer.data)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        """Filter incidents by user's organization"""
        user = self.request.user
        queryset = Incident.objects.filter(deleted_at__isnull=True)

        if user.is_superuser:
            return queryset

        queryset = queryset.filter(organization_id=user.organization_id)

        if user.role == 'end_user':
            return queryset.filter(Q(requester=user) | Q(created_by=user))

        return queryset

    def get_object(self):
        incident = super().get_object()
        user = self.request.user

        if not user.is_superuser and user.role == 'end_user':
            if incident.requester_id != user.id and incident.created_by_id != user.id:
                raise PermissionDenied('End users can only access their own incidents.')

        return incident
    
    def perform_create(self, serializer):
        """Set created_by when creating incident"""
        organization = self._resolve_organization()
        if not organization:
            raise ValidationError({'organization': 'User does not belong to an organization.'})

        requester = serializer.validated_data.get('requester') or self.request.user
        incident = serializer.save(
            organization=organization,
            requester=requester,
            created_by=self.request.user
        )

        if incident.is_major and incident.communication_cadence_minutes:
            incident.next_communication_due = timezone.now() + timedelta(
                minutes=incident.communication_cadence_minutes
            )
            incident.save(update_fields=['next_communication_due'])

        ensure_workflow_instance_for_incident(incident, user=self.request.user)

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
    
    def perform_update(self, serializer):
        """Set updated_by when updating incident"""
        serializer.save(updated_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        incident = self.get_object()
        if incident.update_breach_status():
            incident.save(update_fields=['ola_breach', 'uc_breach', 'sla_breach', 'sla_response_breach'])
        serializer = self.get_serializer(incident)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an incident"""
        incident = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        resolution_code = request.data.get('resolution_code', '')

        if not str(resolution_notes).strip() or not str(resolution_code).strip():
            return Response(
                {'detail': 'Resolution code and notes are required to resolve an incident.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        incident.status = 'resolved'
        incident.resolution_notes = resolution_notes
        incident.resolution_code = resolution_code
        incident.resolved_at = timezone.now()
        incident.save()
        instance = ensure_workflow_instance_for_incident(incident, user=request.user)
        advance_workflow(instance, status='resolved', user=request.user)
        
        return Response({'detail': f'Incident {incident.ticket_number} resolved'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an incident"""
        incident = self.get_object()

        if incident.status != IncidentStatus.RESOLVED:
            return Response(
                {'detail': 'Incident must be resolved before closure.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        incident.status = 'closed'
        incident.closed_at = timezone.now()
        incident.save()

        instance = ensure_workflow_instance_for_incident(incident, user=request.user)
        advance_workflow(instance, status='closed', user=request.user, complete=True)
        
        return Response({'detail': f'Incident {incident.ticket_number} closed'})
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen an incident"""
        incident = self.get_object()
        incident.status = IncidentStatus.REOPENED
        incident.save(update_fields=['status'])

        instance = ensure_workflow_instance_for_incident(incident, user=request.user)
        advance_workflow(instance, status='reopened', user=request.user)

        return Response({'detail': f'Incident {incident.ticket_number} reopened'})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign incident to a user"""
        incident = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        if not assigned_to_id:
            return Response({'detail': 'assigned_to_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        assignee = User.objects.filter(id=assigned_to_id, is_active=True).first()
        if not assignee:
            return Response({'detail': 'Assignee not found or inactive.'}, status=status.HTTP_400_BAD_REQUEST)

        if assignee.role == 'end_user':
            return Response({'detail': 'End users cannot be assigned incidents.'}, status=status.HTTP_400_BAD_REQUEST)

        if incident.organization and assignee.organization:
            if assignee.organization.name != incident.organization.name:
                return Response({'detail': 'Assignee must belong to the same organization.'}, status=status.HTTP_400_BAD_REQUEST)
        elif incident.organization:
            return Response({'detail': 'Assignee must belong to the same organization.'}, status=status.HTTP_400_BAD_REQUEST)

        incident.assigned_to = assignee
        incident.status = 'assigned'
        if incident.first_response_time is None:
            incident.first_response_time = timezone.now()
        incident.save(update_fields=['assigned_to', 'status', 'first_response_time'])
        instance = ensure_workflow_instance_for_incident(incident, user=request.user)
        advance_workflow(instance, status='assigned', user=request.user)
        return Response({'detail': 'Incident assigned'})
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate an incident"""
        incident = self.get_object()
        incident.priority = IncidentPriority.CRITICAL
        incident.sla_escalated = True
        incident.save(update_fields=['priority', 'sla_escalated'])

        instance = ensure_workflow_instance_for_incident(incident, user=request.user)
        advance_workflow(instance, status='escalated', user=request.user)
        
        return Response({'detail': f'Incident {incident.ticket_number} escalated'})
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for an incident"""
        incident = self.get_object()
        comments = incident.incidentcomment_set.all()
        serializer = IncidentCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to incident"""
        incident = self.get_object()
        text = request.data.get('text', '')
        is_internal = bool(request.data.get('is_internal', False))
        if request.user.role == 'end_user':
            is_internal = False

        serializer = IncidentCommentSerializer(data={
            'incident': incident.id,
            'text': text,
            'is_internal': is_internal,
            'created_by': request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_communication(self, request, pk=None):
        """Add communication entry for an incident"""
        incident = self.get_object()
        serializer = IncidentCommunicationSerializer(data={
            'incident': incident.id,
            'channel': request.data.get('channel'),
            'audience': request.data.get('audience'),
            'message': request.data.get('message'),
            'sent_at': request.data.get('sent_at') or timezone.now(),
            'sent_by': request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if incident.is_major and incident.communication_cadence_minutes:
            incident.next_communication_due = timezone.now() + timedelta(
                minutes=incident.communication_cadence_minutes
            )
            incident.save(update_fields=['next_communication_due'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IncidentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for incident comments"""
    queryset = IncidentComment.objects.all()
    serializer_class = IncidentCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['incident', 'is_internal']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'incidents.view',
            'retrieve': 'incidents.view',
            'create': 'incidents.comment',
            'update': 'incidents.comment',
            'partial_update': 'incidents.comment',
            'destroy': 'incidents.comment',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class IncidentWorkaroundViewSet(viewsets.ModelViewSet):
    """ViewSet for incident workarounds"""
    queryset = IncidentWorkaround.objects.all()
    serializer_class = IncidentWorkaroundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['incident']
    search_fields = ['title']

    def get_permissions(self):
        action_map = {
            'list': 'incidents.view',
            'retrieve': 'incidents.view',
            'create': 'incidents.update',
            'update': 'incidents.update',
            'partial_update': 'incidents.update',
            'destroy': 'incidents.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]


class IncidentAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for incident attachments"""
    queryset = IncidentAttachment.objects.all()
    serializer_class = IncidentAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['incident']
    ordering = ['-created_at']

    def get_permissions(self):
        action_map = {
            'list': 'incidents.view',
            'retrieve': 'incidents.view',
            'create': 'incidents.update',
            'update': 'incidents.update',
            'partial_update': 'incidents.update',
            'destroy': 'incidents.update',
        }
        permission = action_map.get(self.action)
        if permission:
            return [permission_required(permission)()]
        return [IsAuthenticated()]
