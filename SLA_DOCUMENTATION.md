# SLA (Service Level Agreement) Module Documentation

## Overview

The SLA module provides comprehensive Service Level Agreement management for enterprise ITSM operations, fully compliant with ITIL v4 standards. It enables organizations to:

- **Define SLA Policies**: Create and manage multiple SLA policies with different coverage models
- **Configure Targets**: Set response and resolution time targets per severity level
- **Manage Escalations**: Define automatic escalation rules and procedures
- **Track Compliance**: Monitor SLA compliance metrics and breach history
- **Auto-escalate**: Automatically escalate tickets based on configured rules

## Features

### 1. SLA Policy Management
- Create policies with flexible applicability (service, category, priority)
- Support for multiple business hour models (24x7, business hours, extended)
- Enable/disable policies for testing or maintenance
- Time-based targets (measured in minutes for precision)

### 2. Severity-Based Targets
- Define separate response and resolution times per severity level (Critical, High, Medium, Low)
- Support for different SLA targets per service or category
- Easy modification without affecting active incidents

### 3. Escalation Rules
- Multi-level escalation (Level 1, 2, 3)
- Escalate to teams or users
- Automatic priority increase on escalation
- Manager notification support
- Custom action descriptions

### 4. Breach Tracking
- Automatic detection of SLA breaches
- Track breach type (response vs resolution)
- Record actual breach duration
- Mark breaches as acknowledged
- Historical breach database for audit

### 5. Compliance Metrics
- Monthly compliance percentage calculation
- Track total incidents vs breached incidents
- Target compliance thresholds (default 95%)
- Identify non-compliant months

### 6. Monitoring Tasks
- **check_sla_breaches()**: Runs every 30 minutes - detects and records breaches
- **send_sla_warnings()**: Runs every 15 minutes - alerts about approaching SLA deadlines
- **process_escalations()**: Runs every 15 minutes - executes escalation rules
- **calculate_sla_compliance()**: Runs daily - calculates monthly metrics

## Installation

### 1. Database Setup
```bash
# Run migrations
cd backend
python manage.py migrate sla
```

### 2. Celery Configuration

Add to your `celery.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-sla-breaches': {
        'task': 'apps.sla.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'send-sla-warnings': {
        'task': 'apps.sla.tasks.send_sla_warnings',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'process-sla-escalations': {
        'task': 'apps.sla.tasks.auto_escalate_tickets',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'calculate-sla-compliance': {
        'task': 'apps.sla.tasks.calculate_sla_compliance',
        'schedule': crontab(hour=23, minute=55),  # Daily at 23:55
    },
}
```

### 3. API Endpoints Registration

The following endpoints are automatically registered:

```
GET    /api/v1/sla/policies/              - List SLA policies
POST   /api/v1/sla/policies/              - Create new policy
GET    /api/v1/sla/policies/{id}/         - Get policy details
PATCH  /api/v1/sla/policies/{id}/         - Update policy
DELETE /api/v1/sla/policies/{id}/         - Delete policy

GET    /api/v1/sla/targets/               - List SLA targets
POST   /api/v1/sla/targets/               - Create new target
GET    /api/v1/sla/targets/{id}/          - Get target details
PATCH  /api/v1/sla/targets/{id}/          - Update target
DELETE /api/v1/sla/targets/{id}/          - Delete target

GET    /api/v1/sla/escalations/           - List escalation rules
POST   /api/v1/sla/escalations/           - Create new rule
GET    /api/v1/sla/escalations/{id}/      - Get rule details
PATCH  /api/v1/sla/escalations/{id}/      - Update rule
DELETE /api/v1/sla/escalations/{id}/      - Delete rule

GET    /api/v1/sla/breaches/              - List SLA breaches (read-only)
GET    /api/v1/sla/metrics/               - List compliance metrics (read-only)
```

## Configuration Guide

### Step 1: Create SLA Policy

Use the Admin Panel → SLA Management → Policies tab:

```
Name: Standard Service Policy
Coverage: 24x7
Response Time: 120 minutes (2 hours)
Resolution Time: 480 minutes (8 hours)
Applies To Priority: (optional)
```

### Step 2: Define Targets by Severity

For the policy created above, add targets:

```
Critical:
  - Response: 30 minutes
  - Resolution: 120 minutes

High:
  - Response: 60 minutes
  - Resolution: 240 minutes

Medium:
  - Response: 120 minutes
  - Resolution: 480 minutes

Low:
  - Response: 480 minutes
  - Resolution: 1440 minutes (24 hours)
```

### Step 3: Configure Escalations

Add escalation rules to the policy:

```
Level 1 (30 minutes):
  - Escalate to: Support Team
  - Notify Managers: Yes
  - Action: Assign to senior agent

Level 2 (60 minutes):
  - Escalate to: Support Manager
  - Notify Managers: Yes
  - Action: Increase priority and notify leadership

Level 3 (120 minutes):
  - Escalate to: Director
  - Notify Managers: Yes
  - Action: Critical escalation
```

### Step 4: Apply Policies to Modules

Configure which SLA policy applies to incidents, service requests, problems, and changes:

```python
# In incident creation
incident.sla_policy = policy
incident.severity = 'high'
incident.response_due_at = policy.targets.filter(severity='high').first().response_due_at
incident.resolution_due_at = policy.targets.filter(severity='high').first().resolution_due_at
incident.save()
```

## Data Models

### SLAPolicy
- `organization`: ForeignKey to Organization
- `name`: Unique policy name
- `description`: Long-form description
- `service`: Optional link to specific Service
- `incident_category`: Optional category filter
- `applies_to_priority`: Optional priority filter
- `response_time`: Target first response (minutes)
- `resolution_time`: Target resolution (minutes)
- `coverage`: 24x7 | business | extended
- `is_active`: Enable/disable the policy

### SLATarget
- `sla_policy`: ForeignKey to SLAPolicy
- `severity`: critical | high | medium | low
- `response_time_minutes`: Target response time
- `resolution_time_minutes`: Target resolution time

### SLAEscalation
- `sla_policy`: ForeignKey to SLAPolicy
- `level`: 1 | 2 | 3 (escalation level)
- `escalate_after_minutes`: When to escalate
- `escalate_to_team`: Optional team recipient
- `escalate_to_user`: Optional user recipient
- `notify_managers`: Boolean flag
- `action_description`: What to do on escalation

### SLABreach
- `organization`: ForeignKey to Organization
- `incident`: OneToOne to Incident
- `service_request`: OneToOne to ServiceRequest
- `sla_policy`: Link to policy
- `breach_type`: response | resolution
- `target_time`: When SLA was due
- `breached_at`: When it was breached
- `breach_duration_minutes`: How late
- `is_acknowledged`: Has it been reviewed

### SLAMetric
- `organization`: ForeignKey to Organization
- `year`: Calendar year
- `month`: Calendar month
- `total_incidents`: Count of incidents that month
- `breached_incidents`: Count breached
- `compliance_percentage`: (total - breached) / total * 100
- `target_compliance`: Target percentage (95%)
- `is_compliant`: compliance_percentage >= target

## Integrations

### Incident Integration

When creating/updating incidents:

```python
from apps.sla.utils import create_sla_record, update_sla_record

# On incident creation
create_sla_record(
    organization=incident.organization,
    ticket_type='incident',
    ticket_id=incident.id,
    priority=incident.priority,
    created_at=incident.created_at
)

# When incident is resolved
update_sla_record(
    organization=incident.organization,
    ticket_type='incident',
    ticket_id=incident.id,
    resolved_at=timezone.now()
)
```

### Service Request Integration

Similar pattern for service requests:

```python
create_sla_record(
    organization=request.organization,
    ticket_type='service_request',
    ticket_id=request.id,
    priority=request.priority
)
```

## Admin UI Features

The SLA Admin panel (/admin/sla) provides:

### Dashboard
- Total policies count
- Active policies count
- Monthly compliance percentage
- Current month breach count

### Policies Tab
- List all SLA policies
- Create new policies
- Edit existing policies
- View policy details
- Delete policies
- Action buttons for each policy

### Targets & Escalations Tab
- Select a policy
- Add response/resolution targets
- View all targets for a policy
- Delete targets
- Add escalation rules
- View escalation rules

### Breaches Tab
- List recent SLA breaches
- Filter by:
  - Breach type (response/resolution)
  - Status (acknowledged/unresolved)
  - SLA policy
- View breach details
- Mark as acknowledged

## Monitoring & Alerts

### SLA Breach Detection
Runs every 30 minutes:
- Scans for incidents/requests past due date
- Creates SLABreach records
- Triggers breach alerts

### SLA Warnings
Runs every 15 minutes:
- Identifies tickets within 60 minutes of breach
- Sends warning notifications
- Alerts relevant teams

### Auto-Escalation
Runs every 15 minutes:
- Applies escalation rules
- Increases ticket priority
- Sends notifications to escalation recipients
- Updates ticket records

### Compliance Calculation
Runs daily at 23:55 UTC:
- Calculates monthly compliance metrics
- Updates SLAMetric records
- Identifies non-compliant months
- Generates reports

## Best Practices

1. **Policy Design**
   - Keep policies simple and clear
   - Use consistent severity levels
   - Document escalation procedures
   - Test with non-production data first

2. **Target Setting**
   - Base targets on organizational capability
   - Consider business hours vs 24x7
   - Build in buffer time
   - Regular review and adjustment

3. **Escalation Rules**
   - Define clear escalation paths
   - Set realistic timeframes
   - Ensure recipients are notified
   - Document actions clearly

4. **Monitoring**
   - Review monthly compliance reports
   - Investigate breaches
   - Identify repeat patterns
   - Adjust policies as needed

5. **Administration**
   - Regular policy reviews (quarterly)
   - Archive old breaches yearly
   - Train agents on SLA impact
   - Communicate changes to users

## Troubleshooting

### Breaches Not Being Detected

1. Check if SLA policy is assigned to tickets
2. Verify `check_sla_breaches` task is running
3. Check Celery logs for errors
4. Ensure database migrations are complete

### Escalations Not Triggering

1. Verify escalation rules are configured
2. Check that `auto_escalate_tickets` task runs
3. Ensure team/user emails are correct
4. Check email configuration

### Compliance Metrics Not Calculating

1. Verify `calculate_sla_compliance` task runs
2. Check that incidents have created_at timestamps
3. Ensure organization exists in database
4. Review logs for SQL errors

## API Examples

### Create SLA Policy
```bash
curl -X POST http://localhost:8000/api/v1/sla/policies/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Premium Support",
    "description": "For enterprise customers",
    "response_time": 60,
    "resolution_time": 240,
    "coverage": "24x7",
    "is_active": true
  }'
```

### Get SLA Metrics
```bash
curl http://localhost:8000/api/v1/sla/metrics/?year=2024&month=2 \
  -H "Authorization: Bearer {token}"
```

### List Breaches
```bash
curl http://localhost:8000/api/v1/sla/breaches/ \
  -H "Authorization: Bearer {token}"
```

## Performance Considerations

- SLA checks run every 30 minutes (adjustable)
- Escalations run every 15 minutes (adjustable)
- Compliance calculation is lightweight (once daily)
- Index on `sla_due_date` for faster queries
- Archive old breaches monthly for performance

## Support

For issues or questions:
1. Check logs: `docker logs itsm_web` or Celery worker logs
2. Review this documentation
3. Check database migrations: `python manage.py showmigrations sla`
4. Contact system administrator
