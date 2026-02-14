"""Celery tasks for user management."""

from celery import shared_task
from .ad_sync import sync_ldap_users


@shared_task(name='apps.users.tasks.sync_ad_users')
def sync_ad_users():
    return sync_ldap_users(source='celery')
