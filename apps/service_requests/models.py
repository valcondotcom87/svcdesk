"""
Service Requests Models - Service fulfillment management
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel, AuditModel


class ServiceCategory(TimeStampedModel):
    """Service categories in the catalog"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='service_categories'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'name']
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return self.name


class Service(TimeStampedModel):
    """Services that can be requested"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='services'
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.CASCADE,
        related_name='services'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    
    # Configuration
    fulfillment_time_hours = models.IntegerField(default=24)
    requires_approval = models.BooleanField(default=False)
    approval_group = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_services'
    )
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['organization', 'name']
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return self.name


class ServiceRequest(AuditModel):
    """User service requests"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='service_requests'
    )
    
    # Identifiers
    ticket_number = models.CharField(max_length=50, unique=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requests'
    )
    
    # People
    requester = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='service_requests'
    )
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    
    # Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('in_progress', 'In Progress'),
        ('pending_fulfillment', 'Pending Fulfillment'),
        ('fulfilled', 'Fulfilled'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        db_index=True
    )
    
    # Timing
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)

    # SLA
    sla_policy = models.ForeignKey(
        'sla.SLAPolicy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests'
    )
    sla_due_date = models.DateTimeField(null=True, blank=True)
    sla_breach = models.BooleanField(default=False)
    
    # Priority
    priority = models.IntegerField(choices=[(1, 'High'), (2, 'Medium'), (3, 'Low')], default=2)

    def update_breach_status(self, now=None):
        now = now or timezone.now()
        closed_statuses = {'fulfilled', 'closed', 'rejected'}
        should_check = self.status not in closed_statuses

        if not self.sla_due_date:
            return False

        breach = self.sla_breach or (should_check and now > self.sla_due_date)
        if breach != self.sla_breach:
            self.sla_breach = breach
            return True

        return False
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['ticket_number']),
            models.Index(fields=['requester', 'status']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"


class ServiceRequestApproval(AuditModel):
    """Multi-level approval workflow for service requests"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    
    # Approval Info
    approval_level = models.IntegerField()
    approver = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests'
    )
    approval_group = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approval_requests'
    )
    
    # Decision
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('escalated', 'Escalated'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['request', 'approval_level']
        ordering = ['approval_level']
        indexes = [
            models.Index(fields=['request', 'status']),
            models.Index(fields=['approver']),
        ]


class ServiceRequestItem(TimeStampedModel):
    """Individual items in a service request"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='items'
    )
    
    item_type = models.CharField(max_length=100)
    quantity = models.IntegerField(default=1)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['created_at']


class ServiceRequestAttachment(AuditModel):
    """Attachments to service requests"""
    request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='service_requests/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()
