# SLA Module - Complete Admin Setup Guide

## Table of Contents
1. [Pre-Installation Checklist](#pre-installation-checklist)
2. [Installation Steps](#installation-steps)
3. [Configuration](#configuration)
4. [Testing](#testing)
5. [Monitoring](#monitoring)
6. [Troubleshooting](#troubleshooting)

## Pre-Installation Checklist

- [ ] Django 4.2+ installed
- [ ] Django REST Framework configured
- [ ] Celery and Beat scheduler installed
- [ ] Redis or RabbitMQ for task queue
- [ ] Database with migrations support
- [ ] Email SMTP configured (for escalation notifications)
- [ ] Admin user account created
- [ ] Organization(s) created in system

## Installation Steps

### 1. Database Migration

The SLA module includes Django models for:
- `SLAPolicy` - Main SLA configuration
- `SLATarget` - Response/resolution times by severity
- `SLAEscalation` - Escalation rules
- `SLABreach` - Breach records
- `SLAMetric` - Compliance metrics

Run migrations:
```bash
cd backend
python manage.py migrate sla
```

Verify migration:
```bash
python manage.py showmigrations sla
# Should show all migrations as [X] (applied)
```

### 2. Celery Configuration

Create/update `backend/config/celery.py`:

```python
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('itsm')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# SLA Scheduled Tasks
app.conf.beat_schedule = {
    'check-sla-breaches': {
        'task': 'apps.sla.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'queue': 'sla_tasks'}
    },
    'send-sla-warnings': {
        'task': 'apps.sla.tasks.send_sla_warnings',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {'queue': 'sla_tasks'}
    },
    'process-sla-escalations': {
        'task': 'apps.sla.tasks.auto_escalate_tickets',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {'queue': 'sla_tasks'}
    },
    'calculate-sla-compliance': {
        'task': 'apps.sla.tasks.calculate_sla_compliance',
        'schedule': crontab(hour=23, minute=55),  # Daily at 23:55 UTC
        'options': {'queue': 'sla_tasks'}
    },
}

# Task configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
```

Start Celery Beat:
```bash
# Terminal 1: Start worker
celery -A config worker -l info -Q default,sla_tasks

# Terminal 2: Start scheduler
celery -A config beat -l info
```

Or in Docker:
```bash
docker-compose up -d celery celery-beat
```

### 3. Email Configuration

For escalation notifications, configure SMTP in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@itsm.local'
```

Test email:
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'This is a test', 'noreply@itsm.local', ['admin@example.com'])
1  # Should return 1 if successful
```

### 4. Initialize Standard Policies

Seed the database with standard SLA policies:

```bash
python manage.py seed_sla_policies
```

Output should show:
```
Processing organization: Default Organization
  ✓ Created policy: Standard Enterprise
    ✓ Created critical target (Response: 30min, Resolution: 120min)
    ✓ Created high target (Response: 60min, Resolution: 240min)
    ✓ Created medium target (Response: 120min, Resolution: 480min)
    ✓ Created low target (Response: 480min, Resolution: 1440min)
  ✓ Created policy: Business Hours
  ✓ Created policy: Premium Support

✓ SLA policies seeding completed successfully
```

To reset policies:
```bash
python manage.py seed_sla_policies --reset
```

## Configuration

### Step 1: Access Admin Panel

1. Log in as administrator
2. Navigate to: **Admin → SLA Management**
3. You should see three tabs:
   - **SLA Policies**
   - **Targets & Escalations**
   - **SLA Breaches**

### Step 2: Review and Customize Policies

#### Standard Enterprise Policy

Default settings:
- Coverage: 24x7
- Response time: 120 minutes (2 hours)
- Resolution time: 480 minutes (8 hours)

To customize:
1. Click the Edit button next to policy
2. Modify times as needed
3. Save changes

#### Customize for Your Organization

Example for high-volume support:
```
Policy: Peak Hours Support
Coverage: Extended (8AM-10PM)
Response: 60 minutes
Resolution: 240 minutes

Targets:
- Critical: Response 15min, Resolution 60min
- High: Response 30min, Resolution 120min
- Medium: Response 60min, Resolution 240min
- Low: Response 120min, Resolution 480min

Escalations:
- Level 1 (30min): Notify team lead
- Level 2 (60min): Notify manager + director
- Level 3 (120min): Page on-call engineer
```

### Step 3: Configure Escalation Rules

1. In **Targets & Escalations** tab:
   - Select a policy
   - Click **"Add Escalation"**

2. Fill in escalation details:
   ```
   Level: 1
   Escalate After: 30 minutes
   Escalate To Team: Support Team
   Notify Managers: Yes
   Action Description: Assign to senior agent, review customer history
   ```

3. Add Level 2 for longer delays (60+ minutes)

4. Add Level 3 for critical escalations (120+ minutes)

### Step 4: Apply Policies to Tickets

#### For Incidents:
In incident creation form, the SLA policy auto-applies based on:
1. Priority level matches
2. Organization matches
3. Policy is marked as active

To manually assign:
```bash
# Django shell
from apps.incidents.models import Incident
from apps.sla.models import SLAPolicy

incident = Incident.objects.get(id=123)
policy = SLAPolicy.objects.get(name='Standard Enterprise')
incident.sla_policy = policy
incident.save()
```

#### For Service Requests:
Same pattern - auto-apply based on priority and organization.

### Step 5: Configure Team Escalations

Ensure your organizations have teams properly configured:

1. **Admin → Organization Management**
2. Add teams if not present:
   - Support Team
   - Support Manager
   - Engineering Team
   - Leadership Team

3. Assign users to teams
4. Configure team emails for notifications

## Testing

### Test 1: Check Policy Creation

```bash
python manage.py shell
>>> from apps.sla.models import SLAPolicy
>>> SLAPolicy.objects.all()
<QuerySet [<SLAPolicy: Standard Enterprise>, <SLAPolicy: Business Hours>, <SLAPolicy: Premium Support>]>
```

### Test 2: Create Test Incident with SLA

```bash
python manage.py shell
>>> from apps.incidents.models import Incident
>>> from apps.sla.models import SLAPolicy
>>> 
>>> policy = SLAPolicy.objects.first()
>>> incident = Incident.objects.create(
...     organization_id=1,
...     ticket_number='TEST-001',
...     title='Test SLA Incident',
...     priority=2,  # High
...     status='new',
...     sla_policy=policy
... )
>>> print(f"Response due: {incident.response_due_at}")
>>> print(f"Resolution due: {incident.resolution_due_at}")
```

### Test 3: Test Escalation Logic

Create an old incident and test scalation:
```bash
>>> from django.utils import timezone
>>> from datetime import timedelta
>>>
>>> incident = Incident.objects.create(
...     organization_id=1,
...     ticket_number='OLD-001',
...     title='Old Incident',
...     priority=2,
...     status='new',
...     created_at=timezone.now() - timedelta(hours=2),
...     sla_policy=policy
... )
>>>
>>> # Run escalation task manually
>>> from apps.sla.tasks import auto_escalate_tickets
>>> result = auto_escalate_tickets()
>>> print(result)
```

### Test 4: Test Breach Detection

```bash
>>> from apps.sla.tasks import check_sla_breaches
>>> result = check_sla_breaches()
>>> print(result)
>>> 
>>> # Check if breach was recorded
>>> from apps.sla.models import SLABreach
>>> SLABreach.objects.filter(incident=incident)
```

### Test 5: Test Email Notifications

```bash
>>> from django.core.mail import send_mail
>>> result = send_mail(
...     'Test',
...     'Email configuration working',
...     'noreply@itsm.local',
...     ['your-email@example.com']
... )
>>> print(f"Mail sent: {result}")  # Should print: Mail sent: 1
```

### Test 6: Check Celery Tasks

Verify tasks are registered:
```bash
# In Django shell
>>> from celery import current_app
>>> current_app.tasks.keys()
# Should include:
# 'apps.sla.tasks.check_sla_breaches'
# 'apps.sla.tasks.send_sla_warnings'
# 'apps.sla.tasks.auto_escalate_tickets'
# 'apps.sla.tasks.calculate_sla_compliance'
```

## Monitoring

### Daily Checks

1. **Check Celery Beat is Running**
   ```bash
   # Check logs
   docker logs itsm_celery_beat
   # Should show "Scheduler: Sending due task check-sla-breaches"
   ```

2. **Verify Task Execution**
   ```bash
   # Check Celery worker logs
   docker logs itsm_celery
   # Should show tasks executing
   ```

3. **Review SLA Dashboard**
   - **Admin → SLA Management**
   - Check statistics:
     - Total policies
     - Active policies
     - Monthly compliance
     - Breach count

### Weekly Checks

1. **Review Breaches**
   - Go to **Admin → SLA Management → Breaches**
   - Look for unacknowledged breaches
   - Investigate patterns

2. **Check Escalations**
   - Are escalations triggering correctly?
   - Are notifications being sent?
   - Review escalation history

3. **Email Verification**
   - Check if escalation emails are reaching recipients
   - Verify SMTP logs

### Monthly Review

1. **Compliance Metrics**
   - API: `/api/v1/sla/metrics/?year=2024&month=2`
   - Review compliance %, breaches, incidents

2. **Policy Review**
   - Are policies meeting organizational needs?
   - Do SLA times need adjustment?
   - Any escalations not being handled?

3. **Team Feedback**
   - Collect feedback from support teams
   - Identify policy gaps
   - Plan adjustments

## Troubleshooting

### Issue: Celery Tasks Not Running

**Symptom**: Tasks not executing, breaches not detected

**Solutions**:
1. Check Celery is running:
   ```bash
   docker ps | grep celery
   # Should show celery and celery-beat containers
   ```

2. Check Beat schedule:
   ```bash
   docker logs itsm_celery_beat | tail -20
   # Should show scheduled tasks
   ```

3. Restart services:
   ```bash
   docker-compose restart celery celery-beat
   ```

4. Check task registration:
   ```bash
   python manage.py shell
   >>> from celery import current_app as app
   >>> [t for t in sorted(app.tasks.keys()) if 'sla' in t]
   ```

### Issue: Policies Not Applying to Incidents

**Symptom**: Incidents created without SLA data

**Solutions**:
1. Verify policy is active:
   ```bash
   python manage.py shell
   >>> from apps.sla.models import SLAPolicy
   >>> SLAPolicy.objects.filter(is_active=True)
   ```

2. Check incident priority matches policy:
   - Policy: `applies_to_priority = 'high'`
   - Incident: `priority = 2` (high)

3. Manually assign SLA:
   ```bash
   incident.sla_policy = policy
   incident.save()
   ```

### Issue: No Email Notifications

**Symptom**: Escalation emails not being sent

**Solutions**:
1. Test email config:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Works!', 'noreply@itsm.local', ['test@example.com'])
   1  # Should return 1
   ```

2. Check SMTP settings in `settings.py`

3. Verify team members have emails:
   ```bash
   >>> from apps.organizations.models import Team
   >>> team = Team.objects.first()
   >>> team.members.values_list('email', flat=True)
   ```

4. Check escalation rule has recipient:
   - Team OR user must be specified
   - Manager notification doesn't replace them

### Issue: Compliance Not Calculating

**Symptom**: No SLA metrics in database

**Solutions**:
1. Run task manually:
   ```bash
   python manage.py shell
   >>> from apps.sla.tasks import calculate_sla_compliance
   >>> result = calculate_sla_compliance()
   >>> print(result)
   ```

2. Check database:
   ```bash
   python manage.py shell
   >>> from apps.sla.models import SLAMetric
   >>> SLAMetric.objects.all()
   ```

3. Verify incidents exist:
   ```bash
   python manage.py shell
   >>> from apps.incidents.models import Incident
   >>> Incident.objects.filter(sla_policy__isnull=False).count()
   ```

### Issue: Breaches Not Being Detected

**Symptom**: Expired SLAs not showing in breaches

**Solutions**:
1. Run check manually:
   ```bash
   python manage.py shell
   >>> from apps.sla.tasks import check_sla_breaches
   >>> result = check_sla_breaches()
   ```

2. Check incident due dates:
   ```bash
   python manage.py shell
   >>> from apps.incidents.models import Incident
   >>> from django.utils import timezone
   >>> now = timezone.now()
   >>> incidents = Incident.objects.filter(
   ...     resolution_due_at__lt=now,
   ...     resolved_at__isnull=True
   ... )
   >>> for i in incidents:
   ...     print(f"{i.ticket_number}: Due {i.resolution_due_at}")
   ```

3. Check SLABreach model has the breach:
   ```bash
   python manage.py shell
   >>> from apps.sla.models import SLABreach
   >>> SLABreach.objects.filter(breach_type='resolution')
   ```

## Performance Optimization

### Task Scheduling
- Adjust frequency based on load
- Reduce `check_sla_breaches` interval if quick detection needed
- Increase interval if system is overloaded

### Database
- Add index to `response_due_at` and `resolution_due_at`:
  ```python
  class Meta:
      indexes = [
          models.Index(fields=['response_due_at']),
          models.Index(fields=['resolution_due_at']),
      ]
  ```

- Archive old breaches monthly

### Email
- Configure bulk email if many escalations
- Use asynchronous email backend
- Set reasonable recipient limits

## Support & Help

- **Documentation**: `SLA_DOCUMENTATION.md`
- **Quick Start**: `SLA_QUICKSTART.md`
- **API Docs**: `/api/schema/sla/`
- **Admin Interface**: `/admin/sla/`
- **Logs**: `docker logs itsm_web` / `docker logs itsm_celery`

For issues, check logs and follow troubleshooting section above.
