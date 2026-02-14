"""Active Directory sync helpers."""

import os
from django.contrib.auth import get_user_model
from django.utils import timezone

try:
    from ldap3 import Server, Connection, ALL, SUBTREE
except ImportError:  # pragma: no cover
    Server = Connection = None

from .models import Organization, ADSyncLog

User = get_user_model()


def _get_setting(name, default=None):
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else value


def sync_ldap_users(triggered_by_id=None, source='manual'):
    log = ADSyncLog.objects.create(triggered_by_id=triggered_by_id, source=source)
    if Server is None or Connection is None:
        log.status = 'failed'
        log.error_message = 'ldap3 is not installed. Add ldap3 to requirements.'
        log.completed_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'completed_at'])
        return {
            'success': False,
            'error': log.error_message
        }

    server_uri = _get_setting('AD_SERVER_URI')
    bind_dn = _get_setting('AD_BIND_DN')
    bind_password = _get_setting('AD_BIND_PASSWORD')
    search_base = _get_setting('AD_SEARCH_BASE')

    if not all([server_uri, bind_dn, bind_password, search_base]):
        log.status = 'failed'
        log.error_message = 'Missing AD configuration. Set AD_SERVER_URI, AD_BIND_DN, AD_BIND_PASSWORD, AD_SEARCH_BASE.'
        log.completed_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'completed_at'])
        return {
            'success': False,
            'error': log.error_message
        }

    user_filter = _get_setting('AD_USER_FILTER', '(objectClass=user)')
    username_attr = _get_setting('AD_USERNAME_ATTR', 'sAMAccountName')
    email_attr = _get_setting('AD_EMAIL_ATTR', 'mail')
    first_name_attr = _get_setting('AD_FIRST_NAME_ATTR', 'givenName')
    last_name_attr = _get_setting('AD_LAST_NAME_ATTR', 'sn')
    default_role = _get_setting('AD_DEFAULT_ROLE', 'end_user')
    org_name = _get_setting('AD_ORGANIZATION', 'Directory Users')
    domain = _get_setting('AD_DOMAIN')

    org, _ = Organization.objects.get_or_create(
        name=org_name,
        defaults={
            'domain': domain,
            'is_active': True,
        }
    )

    try:
        server = Server(server_uri, get_info=ALL)
        conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True)

        conn.search(
            search_base=search_base,
            search_filter=user_filter,
            search_scope=SUBTREE,
            attributes=[username_attr, email_attr, first_name_attr, last_name_attr]
        )

        created = 0
        updated = 0
        skipped = 0

        for entry in conn.entries:
            email = getattr(entry, email_attr, None)
            email_value = str(email.value) if email and email.value else None
            if not email_value:
                skipped += 1
                continue

            username_value = getattr(entry, username_attr, None)
            username = str(username_value.value) if username_value and username_value.value else email_value.split('@')[0]
            first_name_value = getattr(entry, first_name_attr, None)
            last_name_value = getattr(entry, last_name_attr, None)

            defaults = {
                'username': username,
                'first_name': str(first_name_value.value) if first_name_value and first_name_value.value else '',
                'last_name': str(last_name_value.value) if last_name_value and last_name_value.value else '',
                'role': default_role,
                'organization': org,
                'is_active': True,
            }

            user, was_created = User.objects.get_or_create(email=email_value, defaults=defaults)
            if was_created:
                user.set_unusable_password()
                user.save(update_fields=['password'])
                created += 1
            else:
                updates = {
                    'username': defaults['username'],
                    'first_name': defaults['first_name'],
                    'last_name': defaults['last_name'],
                    'role': defaults['role'],
                    'organization': org,
                    'is_active': True,
                }
                User.objects.filter(id=user.id).update(**updates, updated_at=timezone.now())
                updated += 1

        conn.unbind()
    except Exception as exc:
        log.status = 'failed'
        log.error_message = str(exc)
        log.completed_at = timezone.now()
        log.save(update_fields=['status', 'error_message', 'completed_at'])
        return {
            'success': False,
            'error': log.error_message
        }

    log.status = 'success'
    log.created_count = created
    log.updated_count = updated
    log.skipped_count = skipped
    log.completed_at = timezone.now()
    log.save(update_fields=['status', 'created_count', 'updated_count', 'skipped_count', 'completed_at'])

    return {
        'success': True,
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'organization': org.name,
    }
