"""
SLA Utils - Helper functions for SLA calculation
"""
from datetime import timedelta
from django.utils import timezone
from apps.sla.models import SLAPolicy, SLATarget, SLAMetrics


def get_applicable_sla(organization, module, priority):
    """Get applicable SLA target for a ticket"""
    policy = SLAPolicy.objects.filter(
        organization=organization,
        is_active=True,
        applicable_modules__contains=module
    ).first()
    
    if not policy:
        return None
    
    target = SLATarget.objects.filter(
        policy=policy,
        priority=priority
    ).first()
    
    return target


def create_sla_metrics(organization, ticket_type, ticket_id, priority, created_at=None):
    """Create SLA metrics for a new ticket"""
    if created_at is None:
        created_at = timezone.now()
    
    # Get module and SLA policy
    module_map = {
        'incident': 'incidents',
        'service_request': 'service_requests',
        'problem': 'problems',
        'change': 'changes',
    }
    module = module_map.get(ticket_type, ticket_type)
    
    target = get_applicable_sla(organization, module, priority)
    
    if not target:
        return None
    
    # Calculate due dates
    response_due = created_at + timedelta(hours=target.response_time_hours)
    resolution_due = created_at + timedelta(hours=target.resolution_time_hours)
    
    # Create metrics
    metrics = SLAMetrics.objects.create(
        organization=organization,
        ticket_type=ticket_type,
        ticket_id=ticket_id,
        sla_policy=target.policy,
        sla_target=target,
        created_at_override=created_at,
        response_due_at=response_due,
        resolution_due_at=resolution_due,
    )
    
    return metrics


def update_sla_metrics(organization, ticket_type, ticket_id, status=None, resolved=False):
    """Update SLA metrics when ticket status changes"""
    try:
        metrics = SLAMetrics.objects.get(
            organization=organization,
            ticket_type=ticket_type,
            ticket_id=ticket_id
        )
    except SLAMetrics.DoesNotExist:
        return None
    
    now = timezone.now()
    
    # Mark first response
    if not metrics.first_response_at and status in ['assigned', 'acknowledged', 'in_progress']:
        metrics.first_response_at = now
        if metrics.response_due_at and now > metrics.response_due_at:
            metrics.response_breached = True
    
    # Mark resolution
    if resolved and not metrics.resolution_at:
        metrics.resolution_at = now
        if metrics.resolution_due_at and now > metrics.resolution_due_at:
            metrics.resolution_breached = True
    
    metrics.save(update_fields=[
        'first_response_at', 'response_breached',
        'resolution_at', 'resolution_breached'
    ])
    
    return metrics


def check_sla_breaches():
    """Periodic task to check for SLA breaches and trigger escalations"""
    now = timezone.now()
    
    # Check for response breaches that haven't been marked yet
    breached = SLAMetrics.objects.filter(
        response_due_at__lt=now,
        first_response_at__isnull=True,
        response_breached=False
    ).update(response_breached=True)
    
    # Check for resolution breaches
    breached_res = SLAMetrics.objects.filter(
        resolution_due_at__lt=now,
        resolution_at__isnull=True,
        resolution_breached=False
    ).update(resolution_breached=True)
    
    return breached + breached_res
