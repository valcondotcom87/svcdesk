from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
import json
from .models import ImmutableAuditLog
from apps.users.models import User
from apps.incidents.models import Incident


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Auto-log user creation and modifications"""
    if created:
        action = 'create'
        description = f"User created: {instance.email}"
    else:
        action = 'update'
        description = f"User updated: {instance.email}"
    
    ImmutableAuditLog.log_action(
        user=instance,
        action=action,
        content_type=ContentType.objects.get_for_model(User),
        object_id=instance.id,
        object_repr=str(instance),
        severity='medium' if created else 'low',
        description=description,
    )


@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    """Auto-log user deletion"""
    ImmutableAuditLog.log_action(
        user=None,  # User deleted, so no user reference
        action='delete',
        content_type=ContentType.objects.get_for_model(User),
        object_id=instance.id,
        object_repr=str(instance),
        severity='high',
        description=f"User deleted: {instance.email}",
    )


@receiver(post_save, sender=Incident)
def log_incident_changes(sender, instance, created, **kwargs):
    """Auto-log incident creation and modifications"""
    if created:
        action = 'create'
        severity = 'medium'
        description = f"Incident created: {instance.title} (Priority: {instance.priority})"
    else:
        action = 'update'
        # Determine severity based on priority
        if instance.priority in ['critical', 'urgent']:
            severity = 'high'
        else:
            severity = 'medium'
        description = f"Incident updated: {instance.title}"
    
    # Log with incident owner
    ImmutableAuditLog.log_action(
        user=instance.assigned_to if instance.assigned_to else instance.created_by,
        action=action,
        content_type=ContentType.objects.get_for_model(Incident),
        object_id=instance.id,
        object_repr=str(instance),
        severity=severity,
        description=description,
    )


@receiver(post_delete, sender=Incident)
def log_incident_deletion(sender, instance, **kwargs):
    """Auto-log incident deletion"""
    ImmutableAuditLog.log_action(
        user=None,
        action='delete',
        content_type=ContentType.objects.get_for_model(Incident),
        object_id=instance.id,
        object_repr=str(instance),
        severity='critical',
        description=f"Incident deleted: {instance.title}",
    )


def setup_audit_logging():
    """
    Setup audit logging for critical models
    Call this in apps.py ready() method to register all signals
    """
    pass  # Signals are automatically registered when this module is imported
