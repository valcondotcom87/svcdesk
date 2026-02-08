"""
Incident ViewSets - REST API viewsets for incident management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.incidents.models import Incident, IncidentComment, IncidentWorkaround, IncidentAttachment
from apps.incidents.serializers import (
    IncidentListSerializer, IncidentDetailSerializer, IncidentCreateUpdateSerializer,
    IncidentActionSerializer, IncidentCommentSerializer, IncidentWorkaroundSerializer,
    IncidentAttachmentSerializer
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
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return IncidentListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return IncidentCreateUpdateSerializer
        return IncidentDetailSerializer
    
    def get_queryset(self):
        """Filter incidents by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return Incident.objects.filter(deleted_at__isnull=True)
        return Incident.objects.filter(organization_id=user.organization_id, deleted_at__isnull=True)
    
    def perform_create(self, serializer):
        """Set created_by when creating incident"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating incident"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an incident"""
        incident = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        resolution_code = request.data.get('resolution_code', '')
        
        incident.status = 'resolved'
        incident.resolution_notes = resolution_notes
        incident.resolution_code = resolution_code
        incident.resolved_at = timezone.now()
        incident.save()
        
        return Response({'detail': f'Incident {incident.ticket_number} resolved'})
    
    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Close an incident"""
        incident = self.get_object()
        incident.status = 'closed'
        incident.closed_at = timezone.now()
        incident.save()
        
        return Response({'detail': f'Incident {incident.ticket_number} closed'})
    
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen an incident"""
        incident = self.get_object()
        incident.status = 'open'
        incident.save()
        
        return Response({'detail': f'Incident {incident.ticket_number} reopened'})
    
    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign incident to a user"""
        incident = self.get_object()
        assigned_to_id = request.data.get('assigned_to_id')
        
        try:
            incident.assigned_to_id = assigned_to_id
            incident.status = 'assigned'
            incident.save()
            return Response({'detail': 'Incident assigned'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def escalate(self, request, pk=None):
        """Escalate an incident"""
        incident = self.get_object()
        incident.priority = 'critical'
        incident.sla_escalated = True
        incident.save()
        
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
        text = request.data.get('text')
        is_internal = request.data.get('is_internal', False)
        
        comment = IncidentComment.objects.create(
            incident=incident,
            text=text,
            is_internal=is_internal,
            created_by=request.user
        )
        
        serializer = IncidentCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IncidentCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for incident comments"""
    queryset = IncidentComment.objects.all()
    serializer_class = IncidentCommentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['incident', 'is_internal']
    ordering = ['-created_at']


class IncidentWorkaroundViewSet(viewsets.ModelViewSet):
    """ViewSet for incident workarounds"""
    queryset = IncidentWorkaround.objects.all()
    serializer_class = IncidentWorkaroundSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['incident']
    search_fields = ['title']


class IncidentAttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for incident attachments"""
    queryset = IncidentAttachment.objects.all()
    serializer_class = IncidentAttachmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['incident']
    ordering = ['-created_at']
