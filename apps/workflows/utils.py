"""
Workflow helpers for automatic instance creation and transitions.
"""
from django.utils import timezone

from apps.workflows.models import Workflow, WorkflowInstance, WorkflowTransition


def _get_workflow(organization, workflow_type):
    if not organization:
        return None
    return Workflow.objects.filter(
        organization=organization,
        workflow_type=workflow_type,
        is_active=True,
    ).order_by('created_at').first()


def ensure_workflow_instance_for_incident(incident, user=None):
    workflow = _get_workflow(incident.organization, 'incident')
    if not workflow:
        return None
    instance = WorkflowInstance.objects.filter(workflow=workflow, incident=incident).first()
    if instance:
        return instance

    instance = WorkflowInstance.objects.create(
        workflow=workflow,
        incident=incident,
        status='in_progress',
        current_step=1,
        created_by=user,
    )
    _record_transition(instance, status='created', user=user, from_step=0, to_step=1)
    return instance


def ensure_workflow_instance_for_service_request(service_request, user=None):
    workflow = _get_workflow(service_request.organization, 'approval')
    if not workflow:
        return None
    instance = WorkflowInstance.objects.filter(workflow=workflow, service_request=service_request).first()
    if instance:
        return instance

    instance = WorkflowInstance.objects.create(
        workflow=workflow,
        service_request=service_request,
        status='in_progress',
        current_step=1,
        created_by=user,
    )
    _record_transition(instance, status='created', user=user, from_step=0, to_step=1)
    return instance


def ensure_workflow_instance_for_change(change_request, user=None):
    workflow = _get_workflow(change_request.organization, 'change')
    if not workflow:
        return None
    instance = WorkflowInstance.objects.filter(workflow=workflow, change_request=change_request).first()
    if instance:
        return instance

    instance = WorkflowInstance.objects.create(
        workflow=workflow,
        change_request=change_request,
        status='in_progress',
        current_step=1,
        created_by=user,
    )
    _record_transition(instance, status='created', user=user, from_step=0, to_step=1)
    return instance


def advance_workflow(instance, status, user=None, notes=None, complete=False):
    if not instance:
        return None
    total_steps = instance.workflow.steps.count()
    previous_step = instance.current_step
    next_step = instance.current_step

    if total_steps:
        next_step = min(instance.current_step + 1, total_steps)

    if complete or (total_steps and next_step >= total_steps and status in ['approved', 'fulfilled', 'completed']):
        instance.status = 'completed'
        instance.completed_at = timezone.now()
    elif status in ['rejected', 'cancelled']:
        instance.status = 'cancelled'
    else:
        instance.status = 'in_progress'

    instance.current_step = next_step
    instance.updated_by = user
    instance.save(update_fields=['status', 'current_step', 'completed_at', 'updated_by'])

    _record_transition(instance, status=status, user=user, from_step=previous_step, to_step=next_step, notes=notes)
    return instance


def _record_transition(instance, status, user=None, from_step=None, to_step=None, notes=None):
    if not instance:
        return None
    if from_step is None:
        from_step = instance.current_step
    if to_step is None:
        to_step = instance.current_step

    return WorkflowTransition.objects.create(
        workflow_instance=instance,
        from_step=from_step,
        to_step=to_step,
        status=status,
        notes=notes or '',
        created_by=user,
    )
