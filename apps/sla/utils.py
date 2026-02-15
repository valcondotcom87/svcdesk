"""SLA matching and due date helpers."""
from datetime import timedelta
from django.utils import timezone

from apps.sla.models import SLAPolicy, SLATarget
from apps.organizations.models import DepartmentMember


def _priority_to_severity(priority_value, is_incident=True):
    if is_incident:
        mapping = {
            1: 'critical',
            2: 'high',
            3: 'medium',
            4: 'low',
        }
        return mapping.get(priority_value, 'medium')

    mapping = {
        1: 'high',
        2: 'medium',
        3: 'low',
    }
    return mapping.get(priority_value, 'medium')


def _department_match(user, department):
    if not user or not department:
        return False
    return DepartmentMember.objects.filter(user=user, department=department).exists()


def _score_policy(policy):
    score = 0
    for field in (
        'service',
        'service_category',
        'incident_category',
        'applies_to_priority',
        'incident_impact',
        'incident_urgency',
        'requester',
        'requester_department',
    ):
        if getattr(policy, field, None):
            score += 1
    return score


def _select_policy(policies):
    ranked = sorted(policies, key=lambda item: (-item[0], item[1].id))
    return ranked[0][1] if ranked else None


def select_sla_policy_for_incident(incident):
    if not incident.organization_id:
        return None

    policies = SLAPolicy.objects.filter(
        organization_id=incident.organization_id,
        is_active=True,
        applies_to_type='incident',
    )
    candidates = []
    for policy in policies:
        if policy.incident_category and policy.incident_category != (incident.category or ''):
            continue
        if policy.applies_to_priority:
            severity = _priority_to_severity(incident.priority, is_incident=True)
            if policy.applies_to_priority != severity:
                continue
        if policy.incident_impact and policy.incident_impact != incident.impact:
            continue
        if policy.incident_urgency and policy.incident_urgency != incident.urgency:
            continue
        if policy.requester and policy.requester_id != incident.requester_id:
            continue
        if policy.requester_department and not _department_match(incident.requester, policy.requester_department):
            continue
        candidates.append((_score_policy(policy), policy))

    return _select_policy(candidates)


def select_sla_policy_for_service_request(service_request):
    if not service_request.organization_id:
        return None

    policies = SLAPolicy.objects.filter(
        organization_id=service_request.organization_id,
        is_active=True,
        applies_to_type='service_request',
    )
    candidates = []
    for policy in policies:
        if policy.service_id and policy.service_id != service_request.service_id:
            continue
        if policy.service_category_id:
            service_category_id = getattr(service_request.service, 'category_id', None)
            if policy.service_category_id != service_category_id:
                continue
        if policy.applies_to_priority:
            severity = _priority_to_severity(service_request.priority, is_incident=False)
            if policy.applies_to_priority != severity:
                continue
        if policy.requester and policy.requester_id != service_request.requester_id:
            continue
        if policy.requester_department and not _department_match(service_request.requester, policy.requester_department):
            continue
        candidates.append((_score_policy(policy), policy))

    return _select_policy(candidates)


def resolve_sla_targets(policy, severity):
    if not policy:
        return None, None
    target = SLATarget.objects.filter(sla_policy=policy, severity=severity).first()
    if target:
        return target.response_time_minutes, target.resolution_time_minutes
    return policy.response_time, policy.resolution_time


def apply_sla_dates(instance, response_minutes, resolution_minutes, base_time=None):
    if response_minutes is None and resolution_minutes is None:
        return []
    base_time = base_time or timezone.now()
    updated = []
    if response_minutes is not None:
        instance.sla_response_due_date = base_time + timedelta(minutes=response_minutes)
        updated.append('sla_response_due_date')
    if resolution_minutes is not None:
        instance.sla_due_date = base_time + timedelta(minutes=resolution_minutes)
        updated.append('sla_due_date')
    return updated


def apply_sla_pause(instance, should_pause, now=None):
    now = now or timezone.now()
    updated = []
    if should_pause and not instance.sla_paused_at:
        instance.sla_paused_at = now
        updated.append('sla_paused_at')
        return updated

    if not should_pause and instance.sla_paused_at:
        paused_minutes = int((now - instance.sla_paused_at).total_seconds() / 60)
        instance.sla_pause_total_minutes += max(paused_minutes, 0)
        instance.sla_paused_at = None
        if instance.sla_response_due_date:
            instance.sla_response_due_date += timedelta(minutes=paused_minutes)
            updated.append('sla_response_due_date')
        if instance.sla_due_date:
            instance.sla_due_date += timedelta(minutes=paused_minutes)
            updated.append('sla_due_date')
        updated.extend(['sla_pause_total_minutes', 'sla_paused_at'])
    return updated
