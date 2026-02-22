# SLA Module - Quick Start Guide

## 5-Minute Setup

### Step 1: Run Migrations
```bash
cd backend
python manage.py migrate sla
```

### Step 2: Seed Initial Policies (Optional)
```bash
python manage.py seed_sla_policies
```

This creates three standard policies:
- **Standard Enterprise**: 24x7 support
- **Business Hours**: 9AM-5PM support  
- **Premium Support**: Ultra-fast response times

### Step 3: Access SLA Admin Panel

Navigate to:
- Frontend: **Admin → SLA Management**
- API Docs: **http://localhost:8000/api/schema/sla/**

### Step 4: Configure Your First Policy

#### Option A: Via Admin UI
1. Go to **Admin → SLA Management**
2. Click **"New Policy"**
3. Fill in the form:
   - **Name**: e.g., "My Service Policy"
   - **Coverage**: Select 24x7 or business hours
   - **Response Time**: e.g., 120 (minutes)
   - **Resolution Time**: e.g., 480 (minutes)
4. Click Save

#### Option B: Via API
```bash
curl -X POST http://localhost:8000/api/v1/sla/policies/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Policy",
    "coverage": "24x7",
    "response_time": 120,
    "resolution_time": 480,
    "is_active": true
  }'
```

### Step 5: Add Response/Resolution Targets

In **SLA Management → Targets & Escalations**:
1. Select your policy
2. Click **"Add Target"**
3. Add targets for each severity:

| Severity | Response (min) | Resolution (min) |
|----------|---|---|
| Critical | 30 | 120 |
| High | 60 | 240 |
| Medium | 120 | 480 |
| Low | 480 | 1440 |

### Step 6: Configure Escalations (Optional)

1. Click **"Add Escalation"** in same panel
2. Configure escalation rules:

```
Level 1 - After 30 mins:
  → Escalate to: Support Team
  → Notify Managers: Yes

Level 2 - After 60 mins:
  → Escalate to: Support Manager
  → Notify Managers: Yes

Level 3 - After 120 mins:
  → Escalate to: Director
  → Notify Managers: Yes
```

### Step 7: Enable Celery Tasks

Add to your `celery.py`:

```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-sla-breaches': {
        'task': 'apps.sla.tasks.check_sla_breaches',
        'schedule': crontab(minute='*/30'),
    },
    'send-sla-warnings': {
        'task': 'apps.sla.tasks.send_sla_warnings',
        'schedule': crontab(minute='*/15'),
    },
    'auto-escalate-tickets': {
        'task': 'apps.sla.tasks.auto_escalate_tickets',
        'schedule': crontab(minute='*/15'),
    },
    'calculate-sla-compliance': {
        'task': 'apps.sla.tasks.calculate_sla_compliance',
        'schedule': crontab(hour=23, minute=55),
    },
}
```

## Common Tasks

### View SLA Dashboard
- Frontend: **Admin → SLA Management**
- Displays:
  - Total active policies
  - Monthly compliance %
  - Current month breaches
  - Breach and escalation history

### Check for Breaches
- Frontend: **Admin → SLA Management → Breaches Tab**
- Shows all breached tickets
- Filter by status
- Mark as acknowledged

### Generate Compliance Report
- Backend: Access `/api/v1/sla/metrics/?year=2024&month=2`
- Shows:
  - Compliance percentage
  - Total vs breached incidents
  - Compliant/non-compliant status

### View Escalation History
- Frontend: **Incident Detail → SLA Section**
- Shows:
  - All escalations for ticket
  - Escalation timeline
  - Actions taken

## API Quick Reference

### List Policies
```bash
GET /api/v1/sla/policies/
```

### Get Specific Policy
```bash
GET /api/v1/sla/policies/{id}/
```

### Create Policy
```bash
POST /api/v1/sla/policies/
```

### Update Policy
```bash
PATCH /api/v1/sla/policies/{id}/
```

### List Breaches
```bash
GET /api/v1/sla/breaches/
```

### List Metrics
```bash
GET /api/v1/sla/metrics/?year=2024&month=2
```

## Troubleshooting

### My policies aren't applying to tickets
- Check if `is_active=true`
- Verify priorities match
- Check incident's organization matches

### Breaches not appearing
- Run `check_sla_breaches` manually
- Check Celery tasks are running
- Verify incidents have `sla_policy` set

### Escalations not triggering
- Check `auto_escalate_tickets` task
- Verify escalation rule timeframes
- Ensure team/user emails configured

### No compliance metrics
- Run `calculate_sla_compliance` manually
- Check incidents have timestamps
- Verify database migrations complete

## Manual Task Execution

Run tasks manually for testing:

```bash
# Check breaches
docker exec itsm_web python manage.py shell_plus
>>> from apps.sla.tasks import check_sla_breaches
>>> check_sla_breaches()

# Process escalations
>>> from apps.sla.tasks import auto_escalate_tickets
>>> auto_escalate_tickets()

# Calculate compliance
>>> from apps.sla.tasks import calculate_sla_compliance
>>> calculate_sla_compliance()
```

## Standard Catalog

### Enterprise Standard
- Response: 2 hours
- Resolution: 8 hours
- Coverage: 24x7

### Business Day
- Response: 4 hours
- Resolution: 24 hours
- Coverage: Business (9-5)

### Premium
- Response: 15 minutes
- Resolution: 2 hours
- Coverage: 24x7

## Support
- Documentation: `SLA_DOCUMENTATION.md`
- API: `http://localhost:8000/api/schema/sla/`
- Contact: System Administrator
