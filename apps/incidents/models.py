"""
Incidents Models - Core incident management
"""
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel, SoftDeleteModel, AuditModel


class IncidentPriority(models.IntegerChoices):
    """Incident priority levels (ITIL aligned)"""
    CRITICAL = 1, 'Critical'
    HIGH = 2, 'High'
    MEDIUM = 3, 'Medium'
    LOW = 4, 'Low'


class IncidentUrgency(models.IntegerChoices):
    """Incident urgency (ITIL aligned)"""
    HIGH = 1, 'High'
    MEDIUM = 2, 'Medium'
    LOW = 3, 'Low'


class IncidentImpact(models.IntegerChoices):
    """Incident impact on business (ITIL aligned)"""
    HIGH = 1, 'High (Multiple users/departments)'
    MEDIUM = 2, 'Medium (Department level)'
    LOW = 3, 'Low (Single user)'


class IncidentStatus(models.TextChoices):
    """Incident status workflow"""
    NEW = 'new', 'New'
    ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
    ASSIGNED = 'assigned', 'Assigned'
    IN_PROGRESS = 'in_progress', 'In Progress'
    ON_HOLD = 'on_hold', 'On Hold'
    RESOLVED = 'resolved', 'Resolved'
    CLOSED = 'closed', 'Closed'
    REOPENED = 'reopened', 'Reopened'


class MajorIncidentLevel(models.TextChoices):
    MI1 = 'mi1', 'Major 1 (Critical)'
    MI2 = 'mi2', 'Major 2 (High)'
    MI3 = 'mi3', 'Major 3 (Medium)'


class EscalationStatus(models.TextChoices):
    NOT_ESCALATED = 'not_escalated', 'Not Escalated'
    ESCALATED = 'escalated', 'Escalated'
    DE_ESCALATED = 'de_escalated', 'De-escalated'


class PostIncidentReviewStatus(models.TextChoices):
    NOT_REQUIRED = 'not_required', 'Not Required'
    PENDING = 'pending', 'Pending'
    IN_REVIEW = 'in_review', 'In Review'
    COMPLETED = 'completed', 'Completed'


class Incident(AuditModel):
    """
    Core incident ticket model
    Represents a service disruption or issue
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='incidents'
    )
    
    # Identifiers
    ticket_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # People
    requester = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_incidents'
    )
    assigned_to = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    assigned_to_team = models.ForeignKey(
        'organizations.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_incidents'
    )
    
    # Classification
    category = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    affected_service = models.CharField(max_length=255, blank=True)
    
    # Priority & Impact
    priority = models.IntegerField(choices=IncidentPriority.choices, default=IncidentPriority.MEDIUM)
    urgency = models.IntegerField(choices=IncidentUrgency.choices, default=IncidentUrgency.MEDIUM)
    impact = models.IntegerField(choices=IncidentImpact.choices, default=IncidentImpact.LOW)
    
    # Status & Workflow
    status = models.CharField(
        max_length=20,
        choices=IncidentStatus.choices,
        default=IncidentStatus.NEW,
        db_index=True
    )
    is_major = models.BooleanField(default=False)
    major_incident_level = models.CharField(
        max_length=10,
        choices=MajorIncidentLevel.choices,
        null=True,
        blank=True
    )
    escalation_status = models.CharField(
        max_length=20,
        choices=EscalationStatus.choices,
        default=EscalationStatus.NOT_ESCALATED
    )
    major_incident_manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='major_incidents'
    )
    resolution_code = models.CharField(max_length=100, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    # Timing
    first_response_time = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    communication_cadence_minutes = models.IntegerField(default=60)
    next_communication_due = models.DateTimeField(null=True, blank=True)
    
    # SLA
    sla_breach = models.BooleanField(default=False, db_index=True)
    sla_policy = models.ForeignKey(
        'sla.SLAPolicy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    sla_coverage = models.CharField(
        max_length=20,
        choices=[('24x7', '24x7'), ('business', 'Business Hours (9-5)'), ('extended', 'Extended Hours (8-8)')],
        default='24x7'
    )
    sla_response_due_date = models.DateTimeField(null=True, blank=True)
    sla_response_breach = models.BooleanField(default=False)
    sla_due_date = models.DateTimeField(null=True, blank=True)
    sla_escalated = models.BooleanField(default=False)
    sla_paused_at = models.DateTimeField(null=True, blank=True)
    sla_pause_total_minutes = models.IntegerField(default=0)
    ola_target_minutes = models.IntegerField(null=True, blank=True)
    uc_target_minutes = models.IntegerField(null=True, blank=True)
    ola_due_date = models.DateTimeField(null=True, blank=True)
    uc_due_date = models.DateTimeField(null=True, blank=True)
    ola_breach = models.BooleanField(default=False)
    uc_breach = models.BooleanField(default=False)

    # Post-Incident Review (PIR)
    pir_required = models.BooleanField(default=False)
    pir_status = models.CharField(
        max_length=20,
        choices=PostIncidentReviewStatus.choices,
        default=PostIncidentReviewStatus.NOT_REQUIRED
    )
    pir_summary = models.TextField(blank=True)
    pir_notes = models.TextField(blank=True)
    pir_owner = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pir_incidents'
    )
    pir_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Related
    related_problem = models.ForeignKey(
        'problems.Problem',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='linked_incidents'
    )
    change_request = models.ForeignKey(
        'changes.Change',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'priority']),
            models.Index(fields=['ticket_number']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['sla_breach', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.ticket_number} - {self.title}"
    
    def calculate_priority(self):
        """
        Calculate priority based on ITIL Impact x Urgency matrix
        """
        # Priority Matrix (Impact x Urgency)
        priority_matrix = {
            (1, 1): IncidentPriority.CRITICAL,  # High Impact, High Urgency
            (1, 2): IncidentPriority.HIGH,
            (1, 3): IncidentPriority.MEDIUM,
            (2, 1): IncidentPriority.HIGH,
            (2, 2): IncidentPriority.MEDIUM,
            (2, 3): IncidentPriority.LOW,
            (3, 1): IncidentPriority.MEDIUM,
            (3, 2): IncidentPriority.LOW,
            (3, 3): IncidentPriority.LOW,
        }
        self.priority = priority_matrix.get(
            (self.impact, self.urgency),
            IncidentPriority.MEDIUM
        )
        return self.priority

    def update_breach_status(self, now=None):
        now = now or timezone.now()
        should_check = self.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
        if self.sla_paused_at:
            should_check = False
        updated = False

        if self.ola_due_date:
            breach = self.ola_breach or (should_check and now > self.ola_due_date)
            if breach != self.ola_breach:
                self.ola_breach = breach
                updated = True

        if self.uc_due_date:
            breach = self.uc_breach or (should_check and now > self.uc_due_date)
            if breach != self.uc_breach:
                self.uc_breach = breach
                updated = True

        if self.sla_response_due_date:
            breach = self.sla_response_breach or (should_check and now > self.sla_response_due_date)
            if breach != self.sla_response_breach:
                self.sla_response_breach = breach
                updated = True

        if self.sla_due_date:
            breach = self.sla_breach or (should_check and now > self.sla_due_date)
            if breach != self.sla_breach:
                self.sla_breach = breach
                updated = True

        return updated


class IncidentComment(AuditModel):
    """Comments and notes on incidents"""
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    is_internal = models.BooleanField(default=False)  # Not visible to requester
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['incident', 'is_internal']),
        ]


class IncidentWorkaround(AuditModel):
    """Temporary workarounds for incidents"""
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='workarounds'
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    effectiveness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=3)
    
    class Meta:
        ordering = ['-created_at']


class IncidentAttachment(AuditModel):
    """File attachments to incidents"""
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='attachments'
    )
    file = models.FileField(upload_to='incidents/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.IntegerField()


class IncidentCommunication(AuditModel):
    """Major incident communication log"""

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('portal', 'Portal'),
        ('chat', 'Chat'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
    ]

    AUDIENCE_CHOICES = [
        ('internal', 'Internal'),
        ('external', 'External'),
        ('executive', 'Executive'),
    ]

    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name='communications'
    )
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES)
    message = models.TextField()
    sent_at = models.DateTimeField(default=timezone.now)
    sent_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incident_communications'
    )


class IncidentMetric(TimeStampedModel):
    """Track incident metrics for reporting"""
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='incident_metrics'
    )
    incident = models.OneToOneField(
        Incident,
        on_delete=models.CASCADE,
        related_name='metric'
    )
    
    # Timing Metrics
    first_response_time_minutes = models.IntegerField(null=True, blank=True)
    resolution_time_minutes = models.IntegerField(null=True, blank=True)
    total_time_minutes = models.IntegerField(null=True, blank=True)
    
    # ITIL Metrics
    mttr = models.FloatField(null=True, blank=True)  # Mean Time To Resolve
    mtta = models.FloatField(null=True, blank=True)  # Mean Time To Acknowledge
    fcr = models.BooleanField(default=False)  # First Contact Resolution
    
    # Satisfaction
    customer_satisfaction = models.IntegerField(null=True, blank=True)  # 1-5 scale
    
    class Meta:
        indexes = [
            models.Index(fields=['organization', '-created_at']),
        ]
