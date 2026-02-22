# Compliance Module - Quick Start Guide

## 5-Minute Setup

### 1. Install Requirements
```bash
pip install djangorestframework django-filter
```

### 2. Run Migrations
```bash
python manage.py makemigrations compliance
python manage.py migrate compliance
```

### 3. Create Compliance Frameworks
```bash
python manage.py shell
```

```python
from apps.compliance.models import ComplianceFramework
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create frameworks
ComplianceFramework.objects.create(
    framework='ISO27001',
    description='ISO/IEC 27001:2022',
    status='planned',
    responsible_person=user
)
```

### 4. Test API
```bash
# Get compliance summary
curl http://localhost:8000/api/compliance/frameworks/compliance_summary/

# Get audit logs
curl http://localhost:8000/api/compliance/audit-logs/

# Check compliance status
python manage.py check_compliance_status
```

## 10-Minute Deep Dive

### Create Full Compliance Setup

```python
from apps.compliance.models import (
    ComplianceFramework, ComplianceRequirement,
    IncidentResponsePlan, VulnerabilityTracking
)
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()
compliance_officer = User.objects.first()

# 1. Create Framework
iso = ComplianceFramework.objects.create(
    framework='ISO27001',
    description='ISO/IEC 27001:2022 Information Security Management',
    status='in_progress',
    version='1.0',
    progress_percentage=50,
    target_certification_date=timezone.now().date() + timedelta(days=180),
    responsible_person=compliance_officer
)

# 2. Add Requirements
ComplianceRequirement.objects.create(
    framework=iso,
    requirement_id='A.5.1.1',
    title='Information security policies',
    status='in_progress',
    risk_level='high',
    due_date=timezone.now().date() + timedelta(days=30)
)

# 3. Create Incident Response Plan
plan = IncidentResponsePlan.objects.create(
    name='Data Breach Response',
    incident_type='security_breach',
    severity='critical',
    detection_procedures='Monitor access logs',
    initial_response='Isolate affected systems',
    escalation_path='Notify CISO',
    investigation_procedures='Conduct forensics',
    recovery_procedures='Restore from backup',
    primary_contact=compliance_officer
)

# 4. Create Vulnerability
vuln = VulnerabilityTracking.objects.create(
    vulnerability_id='CVE-2024-0001',
    title='SQL Injection',
    affected_system='User Management',
    severity='critical',
    status='open',
    discovery_date=timezone.now().date(),
    discovered_by=compliance_officer,
    target_remediation_date=timezone.now().date() + timedelta(days=7),
    responsible_person=compliance_officer
)

print("✓ Compliance setup complete!")
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/compliance/frameworks/` | GET, POST | List/create frameworks |
| `/api/compliance/frameworks/{id}/` | GET, PUT, DELETE | Framework details |
| `/api/compliance/frameworks/compliance_summary/` | GET | Overall compliance status |
| `/api/compliance/frameworks/{id}/requirements_status/` | GET | Framework requirements |
| `/api/compliance/requirements/` | GET, POST | List/create requirements |
| `/api/compliance/requirements/overdue/` | GET | Overdue requirements |
| `/api/compliance/audit-logs/` | GET | List audit logs (read-only) |
| `/api/compliance/audit-logs/by_user/` | GET | Logs by user |
| `/api/compliance/audit-logs/by_action/` | GET | Logs by action |
| `/api/compliance/audit-logs/critical_events/` | GET | Critical events only |
| `/api/compliance/audit-logs/verify_chain_integrity/` | GET | Verify hash chain |
| `/api/compliance/incident-plans/` | GET, POST | List/create plans |
| `/api/compliance/incident-plans/{id}/` | GET, PUT, DELETE | Plan details |
| `/api/compliance/incident-plans/{id}/test_plan/` | GET | Testing procedures |
| `/api/compliance/incident-plans/review_due/` | GET | Due for review |
| `/api/compliance/vulnerabilities/` | GET, POST | List/create vulnerabilities |
| `/api/compliance/vulnerabilities/open_vulnerabilities/` | GET | Open vulnerabilities |
| `/api/compliance/vulnerabilities/overdue_remediations/` | GET | Overdue remediations |
| `/api/compliance/vulnerabilities/by_severity/` | GET | Filter by severity |
| `/api/compliance/vulnerabilities/remediation_report/` | GET | Remediation metrics |
| `/api/compliance/checkpoints/` | GET, POST | List/create checkpoints |
| `/api/compliance/checkpoints/pending_checkpoints/` | GET | Pending checkpoints |
| `/api/compliance/checkpoints/compliance_score/` | GET | Overall compliance score |
| `/api/compliance/checkpoints/{id}/mark_complete/` | POST | Mark as completed |

## Management Commands

```bash
# Generate compliance report
python manage.py generate_compliance_report --format text

# Verify audit log chain integrity
python manage.py verify_audit_chain --days 30

# Check compliance status
python manage.py check_compliance_status
```

## Django Admin Access

Navigate to:
```
http://localhost:8000/admin/compliance/
```

Available admin interfaces:
- Compliance Frameworks
- Compliance Requirements
- Immutable Audit Logs (read-only)
- Incident Response Plans
- Vulnerability Tracking
- Compliance Checkpoints

## Key Features at a Glance

### 1. Immutable Audit Logging
```python
from apps.compliance.models import ImmutableAuditLog

# Automatically logged via signals, or manually:
log = ImmutableAuditLog.log_action(
    user=request.user,
    action='delete',
    content_type=...,
    object_id=...,
    object_repr='...',
    severity='high',
    description='User account deleted'
)
```

### 2. Hash Chain Verification
```bash
# Verify no audit logs were tampered with
curl http://localhost:8000/api/compliance/audit-logs/verify_chain_integrity/
```

### 3. Compliance Tracking
- Track progress toward certifications
- Manage individual requirements
- Collect evidence
- Track completion dates

### 4. Incident Response
- Formal procedures (detection, response, escalation, investigation, recovery)
- SLA tracking (15min detection, 30min response, 4hr resolution)
- Communication templates

### 5. Vulnerability Management
- CVE tracking
- Remediation planning
- Risk acceptance workflow
- Overdue tracking

## Testing

```bash
# Run all compliance tests
python manage.py test apps.compliance.tests

# Run specific test
python manage.py test apps.compliance.tests.ComplianceFrameworkTestCase

# With coverage
coverage run --source='apps.compliance' manage.py test apps.compliance
coverage report
```

## Troubleshooting

### Issue: Migrations not found
```bash
# Check migration status
python manage.py showmigrations compliance

# Recreate migrations if needed
python manage.py makemigrations compliance --empty --name "fix_name"
```

### Issue: Audit logs not being created
```bash
# Verify signals are loaded
python manage.py shell
>>> from apps.compliance import signals
>>> print("Signals loaded successfully")
```

### Issue: API returns 403 Forbidden
```python
# Ensure user is authenticated
# Get token from admin/api-token-auth/
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/compliance/frameworks/
```

## Configuration

Edit `settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps ...
    'apps.compliance',
]

# Compliance settings
COMPLIANCE_AUDIT_LOG_RETENTION_DAYS = 2555  # ~7 years
COMPLIANCE_HASH_ALGORITHM = 'sha256'
COMPLIANCE_VERIFY_HASH_CHAIN = True
```

## Standards Coverage

✅ **ISO 27001** - Information Security Management
- A.5.1.1: Policies
- A.12.4: Logging & Monitoring
- A.16.1: Incident Response

✅ **NIST CSF** - Cybersecurity Framework
- Identify, Protect, Detect, Respond, Recover

✅ **NIST SP 800-53** - Security Controls
- AU-2, AU-3, AU-12: Audit Controls

✅ **GDPR** - Data Protection Regulation
- Article 32: Security of Processing
- Article 33: Breach Notification

✅ **SOC 2** - Trust Service Criteria
- CC6.1, CC7.1, CC7.2: Logical Access & Change Management

✅ **ISO 20000** - IT Service Management
- Incident Management
- Change Management

## Common Tasks

### Get Overall Compliance Score
```bash
curl http://localhost:8000/api/compliance/checkpoints/compliance_score/
```

### Find Open Vulnerabilities
```bash
curl http://localhost:8000/api/compliance/vulnerabilities/open_vulnerabilities/
```

### Get Critical Audit Events
```bash
curl http://localhost:8000/api/compliance/audit-logs/critical_events/
```

### Review Overdue Requirements
```bash
curl http://localhost:8000/api/compliance/requirements/overdue/
```

### Verify Audit Trail Integrity
```bash
curl http://localhost:8000/api/compliance/audit-logs/verify_chain_integrity/
```

## Next Steps

1. ✅ Install compliance module
2. ✅ Run migrations
3. ✅ Create initial frameworks
4. ✅ Set up audit logging
5. → Create compliance checkpoints
6. → Track vulnerabilities
7. → Setup incident response
8. → Monitor compliance score
9. → Generate compliance reports
10. → Integrate with alerting

## Resources

- **Full Documentation**: See `COMPLIANCE_DOCUMENTATION.md`
- **Settings Guide**: See `COMPLIANCE_SETTINGS.md`
- **Implementation Guide**: See `COMPLIANCE_IMPLEMENTATION_GUIDE.md`
- **API Tests**: See `tests.py`

## Support

- Django Admin: http://localhost:8000/admin/compliance/
- API Docs: http://localhost:8000/api/compliance/
- Logs: `logs/compliance.log`
- Audit Logs: Database `compliance_immutableauditlog` table

---

**Status**: ✅ Ready to use

The compliance module is production-ready and fully functional. Start with the 5-minute setup above, then explore the full capabilities using the API endpoints and management commands.
