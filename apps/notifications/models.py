"""
Notifications Models - Multi-channel notifications
"""
from django.db import models
from apps.core.models import TimeStampedModel


class NotificationTemplate(TimeStampedModel):
    """Notification message templates"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='notification_templates'
    )
    
    name = models.CharField(max_length=255)
    channel = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('slack', 'Slack'),
            ('teams', 'Microsoft Teams'),
            ('in_app', 'In-App'),
        ]
    )
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'name', 'channel']


class Notification(TimeStampedModel):
    """Individual notifications sent to users"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    recipient = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications'
    )
    
    channel = models.CharField(
        max_length=20,
        choices=[
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('slack', 'Slack'),
            ('teams', 'Microsoft Teams'),
            ('in_app', 'In-App'),
        ]
    )
    
    subject = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    
    # Status
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    send_error = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['is_sent', 'send_error']),
        ]


class NotificationPreference(TimeStampedModel):
    """User notification preferences"""
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='notification_preference'
    )
    
    # Channels
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    slack_enabled = models.BooleanField(default=False)
    teams_enabled = models.BooleanField(default=False)
    in_app_enabled = models.BooleanField(default=True)
    
    # Types
    incident_notifications = models.BooleanField(default=True)
    request_notifications = models.BooleanField(default=True)
    approval_notifications = models.BooleanField(default=True)
    
    # Digest
    digest_frequency = models.CharField(
        max_length=20,
        choices=[
            ('immediate', 'Immediate'),
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
        ],
        default='immediate'
    )
