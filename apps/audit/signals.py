"""
Audit logging signals
"""
import json
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict

from apps.audit.models import AuditLog, ComplianceCheck, DataRetentionPolicy
from apps.core.middleware import get_current_request, get_current_user
from apps.organizations.models import Organization


SKIP_APP_LABELS = {'admin', 'contenttypes', 'sessions'}
SKIP_MODELS = {AuditLog, ComplianceCheck, DataRetentionPolicy}


def _serialize_value(value):
    if value is None:
        return None
    return str(value)


def _get_organization(instance):
    organization = getattr(instance, 'organization', None)
    if organization:
        if isinstance(organization, Organization):
            return organization
        org_id = getattr(organization, 'id', None)
        if org_id:
            return Organization.objects.filter(id=org_id).first()
        return None
    organization_id = getattr(instance, 'organization_id', None)
    if not organization_id:
        return None
    return Organization.objects.filter(id=organization_id).first()


def _collect_fields(instance):
    return [field.name for field in instance._meta.fields]


def _get_request_context():
    request = get_current_request()
    if not request:
        return None, None
    return request.META.get('REMOTE_ADDR'), request.META.get('HTTP_USER_AGENT', '')


def _should_skip(sender):
    if sender in SKIP_MODELS:
        return True
    if sender._meta.app_label in SKIP_APP_LABELS:
        return True
    return False


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    if _should_skip(sender):
        return
    if not instance.pk:
        return
    old_values = sender.objects.filter(pk=instance.pk).values().first()
    if old_values:
        instance._audit_old_values = old_values


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if _should_skip(sender):
        return
    organization = _get_organization(instance)
    if not organization:
        return

    user = get_current_user()
    ip_address, user_agent = _get_request_context()

    new_values = model_to_dict(instance, fields=_collect_fields(instance))
    old_values = getattr(instance, '_audit_old_values', {})

    if created:
        changes_old = {}
        changes_new = {key: _serialize_value(value) for key, value in new_values.items()}
        action = 'created'
    else:
        changes_old = {}
        changes_new = {}
        for key, new_value in new_values.items():
            old_value = old_values.get(key)
            if old_value != new_value:
                changes_old[key] = _serialize_value(old_value)
                changes_new[key] = _serialize_value(new_value)
        if not changes_new:
            return
        action = 'updated'

    AuditLog.objects.create(
        organization=organization,
        user=user,
        action=action,
        entity_type=sender.__name__,
        entity_id=str(instance.pk),
        field_name='',
        old_value=json.dumps(changes_old, default=str),
        new_value=json.dumps(changes_new, default=str),
        ip_address=ip_address,
        user_agent=user_agent or '',
        status='success',
    )


@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if _should_skip(sender):
        return
    organization = _get_organization(instance)
    if not organization:
        return

    user = get_current_user()
    ip_address, user_agent = _get_request_context()
    values = model_to_dict(instance, fields=_collect_fields(instance))

    AuditLog.objects.create(
        organization=organization,
        user=user,
        action='deleted',
        entity_type=sender.__name__,
        entity_id=str(instance.pk),
        field_name='',
        old_value=json.dumps({key: _serialize_value(value) for key, value in values.items()}, default=str),
        new_value='{}',
        ip_address=ip_address,
        user_agent=user_agent or '',
        status='success',
    )
