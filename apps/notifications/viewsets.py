"""
Notification ViewSets - REST API viewsets for notification management
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.notifications.models import (
    Notification, NotificationTemplate, NotificationChannel, NotificationLog
)
from apps.notifications.serializers import (
    NotificationListSerializer, NotificationDetailSerializer,
    NotificationCreateUpdateSerializer, BulkNotificationSerializer,
    NotificationTemplateSerializer, NotificationChannelSerializer,
    NotificationLogSerializer
)


class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for notifications"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipient', 'is_read']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NotificationCreateUpdateSerializer
        return NotificationDetailSerializer
    
    def get_queryset(self):
        """Get notifications for current user"""
        return Notification.objects.filter(recipient=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_send(self, request):
        """Send notification to multiple users"""
        serializer = BulkNotificationSerializer(data=request.data)
        if serializer.is_valid():
            recipient_ids = serializer.validated_data['recipient_ids']
            title = serializer.validated_data['title']
            message = serializer.validated_data['message']
            notification_type = serializer.validated_data['notification_type']
            priority = serializer.validated_data.get('priority', 'normal')
            data = serializer.validated_data.get('data', {})
            
            from apps.core.models import CustomUser
            users = CustomUser.objects.filter(id__in=recipient_ids)
            
            notifications = [
                Notification(
                    recipient=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    data=data
                )
                for user in users
            ]
            
            Notification.objects.bulk_create(notifications)
            return Response({'detail': f'Notifications sent to {len(notifications)} users'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'detail': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_as_read(self, request):
        """Mark all notifications as read"""
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return Response({'detail': 'All notifications marked as read'})


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for notification templates"""
    queryset = NotificationTemplate.objects.filter(is_active=True)
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'event_type']
    search_fields = ['name']
    
    def get_queryset(self):
        """Filter by user's organization"""
        user = self.request.user
        if user.is_superuser:
            return NotificationTemplate.objects.filter(is_active=True)
        return NotificationTemplate.objects.filter(organization_id=user.organization_id, is_active=True)


class NotificationChannelViewSet(viewsets.ModelViewSet):
    """ViewSet for notification channels"""
    queryset = NotificationChannel.objects.filter(is_active=True)
    serializer_class = NotificationChannelSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for notification logs"""
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipient', 'channel', 'status']
    ordering = ['-sent_at']
