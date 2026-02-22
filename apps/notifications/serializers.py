"""
Notification Serializers - REST API serializers for notification management
"""
from rest_framework import serializers
from apps.notifications.models import (
    Notification, NotificationTemplate, NotificationChannel, NotificationLog
)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for notification templates"""
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'organization', 'name', 'description', 'event_type',
            'subject_template', 'body_template', 'is_active'
        ]


class NotificationChannelSerializer(serializers.ModelSerializer):
    """Serializer for notification channels"""
    class Meta:
        model = NotificationChannel
        fields = [
            'id', 'name', 'channel_type', 'is_active', 'configuration'
        ]


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'recipient', 'recipient_name', 'channel', 'channel_display',
            'subject', 'message', 'status', 'status_display', 'sent_at', 'read_at'
        ]


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight notification list serializer"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name', 'title', 'message',
            'is_read', 'created_at'
        ]


class NotificationDetailSerializer(serializers.ModelSerializer):
    """Full notification detail serializer"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name', 'title', 'message',
            'notification_type', 'priority', 'priority_display', 'data',
            'is_read', 'read_at', 'created_at'
        ]
        read_only_fields = ['created_at']


class NotificationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating notifications"""
    class Meta:
        model = Notification
        fields = ['recipient', 'title', 'message', 'notification_type', 'priority', 'data']


class BulkNotificationSerializer(serializers.Serializer):
    """Serializer for sending bulk notifications"""
    recipient_ids = serializers.ListField(child=serializers.IntegerField())
    title = serializers.CharField()
    message = serializers.CharField()
    notification_type = serializers.CharField()
    priority = serializers.CharField(default='normal')
    data = serializers.JSONField(required=False)
