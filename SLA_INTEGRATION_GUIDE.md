# SLA Integration Guide

## Overview

This guide explains how to integrate SLA functionality into your existing incident, service request, problem, and change management workflows.

## Integration Points

### 1. Incident Workflow Integration

When an incident is created with a priority level, the system automatically:
1. Finds matching SLA policy
2. Calculates response and resolution due dates
3. Records SLA metrics
4. Schedules monitoring for breaches and escalations

#### Backend Integration

**In `apps/incidents/signals.py` or `viewsets.py`:**

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.sla.utils import create_sla_record, update_sla_record
from apps.incidents.models import Incident

# Auto-create SLA record when incident is created
@receiver(post_save, sender=Incident)
def create_incident_sla(sender, instance, created, **kwargs):
    if created and instance.sla_policy:
        create_sla_record(
            organization=instance.organization,
            ticket_type='incident',
            ticket_id=instance.id,
            priority=instance.priority,
            created_at=instance.created_at
        )

# Update SLA when incident is resolved
def resolve_incident(request, incident_id):
    incident = Incident.objects.get(id=incident_id)
    incident.status = 'resolved'
    incident.resolved_at = timezone.now()
    incident.save()
    
    # Update SLA metrics
    update_sla_record(
        organization=incident.organization,
        ticket_type='incident',
        ticket_id=incident.id,
        status='resolved'
    )
    
    return Response({'status': 'resolved'})
```

#### Frontend Integration

**In `fe/src/pages/IncidentDetail.jsx`:**

```jsx
import SLAMetricsWidget from '../components/SLAMetricsWidget';

export default function IncidentDetail() {
  const [incident, setIncident] = useState(null);
  
  return (
    <div className="incident-detail">
      <h1>{incident?.title}</h1>
      
      {/* Incident details */}
      
      {/* Add SLA Metrics Widget */}
      <SLAMetricsWidget 
        ticketId={incident?.id} 
        ticketType="incident" 
      />
      
      {/* Incident comments/timeline */}
    </div>
  );
}
```

### 2. Service Request Workflow Integration

Similar to incidents - auto-apply SLA policies:

```python
# In service_requests/signals.py

@receiver(post_save, sender=ServiceRequest)
def create_service_request_sla(sender, instance, created, **kwargs):
    if created:
        # Find matching policy
        from apps.sla.models import SLAPolicy
        
        policy = SLAPolicy.objects.filter(
            organization=instance.organization,
            is_active=True,
            service=instance.service
        ).first()
        
        if policy:
            instance.sla_policy = policy
            instance.save(update_fields=['sla_policy'])
            
            create_sla_record(...)
```

### 3. Problem Workflow Integration

```python
# In problems/signals.py

@receiver(post_save, sender=Problem)
def create_problem_sla(sender, instance, created, **kwargs):
    if created:
        policy = SLAPolicy.objects.filter(
            organization=instance.organization,
            is_active=True,
            applicable_modules__contains='problems'
        ).first()
        
        if policy:
            instance.sla_policy = policy
            instance.save(update_fields=['sla_policy'])
```

### 4. Change Management Workflow Integration

```python
# In changes/signals.py

@receiver(post_save, sender=Change)
def create_change_sla(sender, instance, created, **kwargs):
    if created:
        # Changes have different SLA targets
        policy = SLAPolicy.objects.filter(
            organization=instance.organization,
            is_active=True,
            applicable_modules__contains='changes'
        ).first()
        
        if policy:
            instance.sla_policy = policy
            instance.save(update_fields=['sla_policy'])
```

## Database Fields to Add

### Add to Incident Model

```python
class Incident(models.Model):
    # ... existing fields ...
    
    # SLA Fields
    sla_policy = models.ForeignKey(
        'sla.SLAPolicy',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incidents'
    )
    
    # Timeline tracking
    first_response_at = models.DateTimeField(null=True, blank=True)
    response_due_at = models.DateTimeField(null=True, blank=True)
    resolution_due_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    sla_response_breached = models.BooleanField(default=False)
    sla_resolution_breached = models.BooleanField(default=False)
    
    # Escalation tracking
    escalation_level = models.IntegerField(default=0)
    escalated_at = models.DateTimeField(null=True, blank=True)
    escalation_count = models.IntegerField(default=0)
```

Create migration:
```bash
python manage.py makemigrations incidents
python manage.py migrate incidents
```

### Add to ServiceRequest Model

Same fields as above.

## Utility Functions

**In `apps/sla/utils.py`:**

```python
from datetime import timedelta
from django.utils import timezone
from apps.sla.models import SLAPolicy, SLABreach

def get_sla_policy(organization, module, priority=None):
    """Find applicable SLA policy"""
    filters = {
        'organization': organization,
        'is_active': True,
    }
    
    if priority:
        filters['applies_to_priority__in'] = [priority, '']
    
    return SLAPolicy.objects.filter(**filters).first()

def assign_sla_to_ticket(ticket, policy=None):
    """Assign SLA policy and calculate due dates"""
    if not policy:
        policy = get_sla_policy(
            ticket.organization,
            ticket.__class__.__name__.lower(),
            getattr(ticket, 'priority', None)
        )
    
    if not policy:
        return None
    
    ticket.sla_policy = policy
    
    # Get target for this priority
    target = policy.targets.filter(
        severity=getattr(ticket, 'priority_display', '').lower()
    ).first()
    
    if target:
        now = timezone.now()
        ticket.response_due_at = now + timedelta(minutes=target.response_time_minutes)
        ticket.resolution_due_at = now + timedelta(minutes=target.resolution_time_minutes)
    
    ticket.save()
    return policy

def mark_first_response(ticket):
    """Record when ticket received first response"""
    if not ticket.first_response_at:
        ticket.first_response_at = timezone.now()
        ticket.save(update_fields=['first_response_at'])

def mark_resolved(ticket):
    """Mark ticket as resolved and check SLA compliance"""
    now = timezone.now()
    ticket.resolved_at = now
    
    # Check for breach
    if ticket.resolution_due_at and now > ticket.resolution_due_at:
        ticket.sla_resolution_breached = True
    
    ticket.save(update_fields=['resolved_at', 'sla_resolution_breached'])

def check_escalation_needed(ticket):
    """Check if ticket needs escalation based on SLA rules"""
    if not ticket.sla_policy:
        return None
    
    now = timezone.now()
    escalations = ticket.sla_policy.escalations.all().order_by('level')
    
    for escalation in escalations:
        escalation_time = ticket.created_at + timedelta(
            minutes=escalation.escalate_after_minutes
        )
        
        if now > escalation_time and ticket.escalation_level < escalation.level:
            return escalation
    
    return None
```

## API Integration

### Include SLA Data in List/Detail Endpoints

**In incident serializers:**

```python
from rest_framework import serializers
from apps.sla.serializers import SLAPolicyListSerializer

class IncidentDetailSerializer(serializers.ModelSerializer):
    sla_policy_details = SLAPolicyListSerializer(
        source='sla_policy',
        read_only=True
    )
    
    class Meta:
        model = Incident
        fields = [
            # ... existing fields ...
            'sla_policy',
            'sla_policy_details',
            'first_response_at',
            'response_due_at',
            'resolution_due_at',
            'resolved_at',
            'sla_response_breached',
            'sla_resolution_breached',
            'escalation_level',
            'escalated_at',
        ]
```

### Add SLA Actions

```python
# In incident viewsets

from rest_framework.decorators import action
from rest_framework.response import Response

class IncidentViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    
    @action(detail=True, methods=['post'])
    def mark_responded(self, request, pk=None):
        """Mark incident as having first response"""
        incident = self.get_object()
        mark_first_response(incident)
        return Response({'status': 'First response recorded'})
    
    @action(detail=True, methods=['post'])
    def check_sla_status(self, request, pk=None):
        """Get current SLA status"""
        incident = self.get_object()
        needed = check_escalation_needed(incident)
        
        return Response({
            'sla_policy': incident.sla_policy.name if incident.sla_policy else None,
            'response_due_at': incident.response_due_at,
            'resolution_due_at': incident.resolution_due_at,
            'response_breached': incident.sla_response_breached,
            'escalation_needed': needed is not None,
            'next_escalation': f"Level {needed.level}" if needed else None,
        })
```

## Frontend Components

### SLA Status Badge

```jsx
// components/SLAStatusBadge.jsx
import { Tag, Tooltip } from 'antd';
import dayjs from 'dayjs';

export default function SLAStatusBadge({ ticket }) {
  if (!ticket.sla_policy_details) {
    return <Tag>No SLA</Tag>;
  }

  const now = dayjs();
  const responseDue = dayjs(ticket.response_due_at);
  const resolutionDue = dayjs(ticket.resolution_due_at);

  let status = 'processing';
  if (ticket.sla_response_breached) status = 'error';
  if (ticket.first_response_at) status = 'success';

  let color = 'blue';
  if (status === 'error') color = 'red';
  if (status === 'success') color = 'green';

  return (
    <Tooltip 
      title={`Response due: ${responseDue.format('DD/MM HH:mm')} | Resolution due: ${resolutionDue.format('DD/MM HH:mm')}`}
    >
      <Tag color={color}>
        {ticket.sla_policy_details.name}
      </Tag>
    </Tooltip>
  );
}
```

### SLA Timeline

```jsx
// components/SLATimeline.jsx
import { Timeline, Tag } from 'antd';
import { CheckCircleOutlined, ExclamationOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';

export default function SLATimeline({ ticket }) {
  const events = [
    {
      date: dayjs(ticket.created_at),
      label: 'Ticket Created',
      icon: <CheckCircleOutlined style={{ color: 'green' }} />,
    },
  ];

  if (ticket.first_response_at) {
    events.push({
      date: dayjs(ticket.first_response_at),
      label: 'First Response',
      icon: <CheckCircleOutlined style={{ color: 'blue' }} />,
    });
  }

  if (ticket.resolved_at) {
    events.push({
      date: dayjs(ticket.resolved_at),
      label: 'Resolved',
      icon: <CheckCircleOutlined style={{ color: 'green' }} />,
    });
  }

  return (
    <Timeline
      items={events.map(event => ({
        label: event.date.format('DD/MM/YYYY HH:mm'),
        children: event.label,
        color: 'green',
      }))}
    />
  );
}
```

## Testing SLA Integration

```python
# tests/test_sla_integration.py

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.incidents.models import Incident
from apps.sla.models import SLAPolicy, SLATarget
from apps.sla.utils import assign_sla_to_ticket

class SLAIntegrationTest(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org')
        self.policy = SLAPolicy.objects.create(
            organization=self.org,
            name='Test Policy',
            response_time=120,
            resolution_time=480,
        )
        SLATarget.objects.create(
            sla_policy=self.policy,
            severity='high',
            response_time_minutes=60,
            resolution_time_minutes=240,
        )

    def test_sla_assigned_on_incident_create(self):
        """Test SLA is automatically assigned"""
        incident = Incident.objects.create(
            organization=self.org,
            title='Test',
            priority=2,  # High
            status='new',
            sla_policy=self.policy,
        )
        
        self.assertIsNotNone(incident.response_due_at)
        self.assertIsNotNone(incident.resolution_due_at)

    def test_sla_breach_detection(self):
        """Test breach is detected when ticket expires"""
        # Create old incident
        past = timezone.now() - timedelta(hours=3)
        incident = Incident.objects.create(
            organization=self.org,
            title='Old Incident',
            priority=2,
            status='new',
            created_at=past,
            sla_policy=self.policy,
            response_due_at=past + timedelta(hours=1),
            first_response_at=None,
        )
        
        # Run check
        from apps.sla.tasks import check_sla_breaches
        result = check_sla_breaches()
        
        # Verify breach recorded
        incident.refresh_from_db()
        self.assertTrue(incident.sla_response_breached)
```

## Monitoring Integration

Monitor SLA health in your dashboards:

```python
# In admin dashboard view

from apps.sla.models import SLABreach, SLAMetric

def dashboard_sla_metrics():
    now = timezone.now()
    
    return {
        'recent_breaches': SLABreach.objects.filter(
            created_at__gte=now - timedelta(days=7)
        ).count(),
        'current_month_compliance': SLAMetric.objects.filter(
            year=now.year,
            month=now.month,
        ).first(),
        'at_risk_tickets': Incident.objects.filter(
            resolution_due_at__lte=now + timedelta(hours=2),
            resolution_due_at__gte=now,
            resolved_at__isnull=True,
        ).count(),
    }
```

## Summary

SLA integration provides:
- ✅ Automatic policy assignment
- ✅ Due date calculation
- ✅ Response and resolution tracking
- ✅ Automatic escalation
- ✅ Breach detection and notification
- ✅ Compliance reporting
- ✅ Team visibility and alerts

For detailed API and admin documentation, see:
- `SLA_DOCUMENTATION.md`
- `SLA_ADMIN_SETUP.md`
- `SLA_QUICKSTART.md`
