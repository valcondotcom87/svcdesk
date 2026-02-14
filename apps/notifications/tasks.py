"""
Notification background tasks.
"""
from celery import shared_task
from django.utils import timezone

from apps.notifications.models import Notification


@shared_task
def cleanup_old_notifications(days=90):
    cutoff = timezone.now() - timezone.timedelta(days=days)
    deleted, _ = Notification.objects.filter(created_at__lt=cutoff).delete()
    return {"deleted": deleted}
