"""
Workflows Models - Workflow automation and multi-step processes
"""
from django.db import models
from apps.core.models import TimeStampedModel, AuditModel


class Workflow(AuditModel):
    """Define workflows for various processes"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='workflows'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    workflow_type = models.CharField(
        max_length=50,
        choices=[
            ('approval', 'Approval'),
            ('fulfillment', 'Fulfillment'),
            ('incident', 'Incident'),
            ('change', 'Change'),
        ]
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['name']


class WorkflowStep(TimeStampedModel):
    """Steps in a workflow"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    
    step_number = models.IntegerField()
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Who can perform this step
    assigned_to_team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='workflow_steps'
    )
    
    # Conditions
    requires_approval = models.BooleanField(default=False)
    approval_count = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['workflow', 'step_number']
        ordering = ['step_number']


class WorkflowInstance(AuditModel):
    """Instance of a workflow execution"""
    workflow = models.ForeignKey(
        Workflow,
        on_delete=models.CASCADE,
        related_name='instances'
    )
    
    # Related Entity
    incident = models.ForeignKey(
        'incidents.Incident',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='workflow_instances'
    )
    service_request = models.ForeignKey(
        'service_requests.ServiceRequest',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='workflow_instances'
    )
    change_request = models.ForeignKey(
        'changes.Change',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='workflow_instances'
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    current_step = models.IntegerField(default=1)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']


class WorkflowTransition(AuditModel):
    """Track workflow step transitions"""
    workflow_instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        related_name='transitions'
    )
    
    from_step = models.IntegerField()
    to_step = models.IntegerField()
    status = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
