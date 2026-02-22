# ITSM System - Quick Reference Guide
## Essential Information at Your Fingertips

---

## 1. QUICK START (For Developers)

### Clone & Setup (5 minutes)
```bash
# Clone backend
git clone https://github.com/company/itsm-backend.git
cd itsm-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser

# Run server
python manage.py runserver 0.0.0.0:8000

# Clone frontend
git clone https://github.com/company/itsm-frontend.git
cd itsm-frontend
npm install
npm start  # http://localhost:3000
```

### Access Points
| Component | URL | Default Credentials |
|-----------|-----|-------------------|
| Backend API | http://localhost:8000/api/v1 | - |
| API Docs | http://localhost:8000/api/v1/docs | - |
| Admin Panel | http://localhost:8000/admin | superuser |
| Frontend | http://localhost:3000 | test@test.com / password |

---

## 2. CORE ENTITIES & RELATIONSHIPS

### Hierarchy
```
Organization
  └─ Users (staff, agents, end_users)
  └─ Teams
  └─ Services
  └─ Tickets (base class)
       ├─ Incidents
       ├─ Service Requests
       ├─ Problems
       ├─ Changes
       └─ Tasks
  └─ CMDB (Configuration Items)
  └─ SLA Policies
```

### Key Model Properties
```python
# Every entity has:
- id: UUID (primary key)
- organization_id: UUID (for multi-tenancy)
- created_at, updated_at: TIMESTAMP
- created_by, updated_by: FK to users
- deleted_at: TIMESTAMP (soft delete)

# Every ticket has:
- ticket_number: VARCHAR (unique per org)
- status: VARCHAR (enum)
- priority: VARCHAR (critical|high|medium|low)
- sla_response_due, sla_resolution_due: TIMESTAMP
- assigned_to_id, assigned_to_team_id: FK
```

---

## 3. PRIORITY CALCULATION MATRIX

| Impact\Urgency | High | Medium | Low |
|----------------|------|--------|-----|
| **High** | 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM |
| **Medium** | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW |
| **Low** | 🟡 MEDIUM | 🟢 LOW | 🟢 LOW |

**Impact Scoring:**
- High (100): Affects critical services or many users (>100)
- Medium (50): Affects important services or some users (10-100)
- Low (10): Affects minor services or few users (<10)

**Urgency Scoring:**
- High (100): Needs resolution within hours
- Medium (50): Needs resolution within 1-2 days
- Low (10): Can wait for scheduled maintenance

---

## 4. SLA TIME CALCULATION

### Business Hours
- Default: 8 AM - 6 PM (10 hours/day)
- Weekends: Excluded
- Holidays: Excluded (configurable)

### Example Calculation
```
Created: Friday 5 PM
SLA: 4 hours (business hours only)
Calculation:
  Friday: 1 hour (5 PM - 6 PM)
  Monday: 3 hours (8 AM - 11 AM)
Due: Monday 11 AM

Created: Friday 5 PM
SLA: 4 hours (calendar hours)
Calculation: 
  Exactly 4 hours later = Saturday 1 AM
Due: Saturday 1 AM
```

---

## 5. API ENDPOINT QUICK REFERENCE

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/incidents` | Create incident |
| GET | `/api/v1/incidents` | List incidents (with filters) |
| GET | `/api/v1/incidents/{id}` | Get incident details |
| PUT | `/api/v1/incidents/{id}` | Update incident |
| POST | `/api/v1/incidents/{id}/resolve` | Mark as resolved |
| POST | `/api/v1/incidents/{id}/close` | Close incident |
| POST | `/api/v1/incidents/{id}/comments` | Add comment |

### Service Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/service-requests` | Create request |
| GET | `/api/v1/service-requests` | List requests |
| POST | `/api/v1/service-requests/{id}/approve` | Approve |
| POST | `/api/v1/service-requests/{id}/reject` | Reject |

### Problems
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/problems` | Create problem |
| POST | `/api/v1/problems/{id}/rca` | Add RCA |
| POST | `/api/v1/kedb` | Create known error |
| GET | `/api/v1/kedb` | Search known errors |

### Changes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/changes` | Create change |
| POST | `/api/v1/changes/{id}/submit` | Submit for approval |
| POST | `/api/v1/changes/{id}/approve` | Approve change |
| POST | `/api/v1/changes/{id}/implement` | Start implementation |
| POST | `/api/v1/changes/{id}/complete` | Complete change |

### CMDB
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/cmdb/configuration-items` | Create CI |
| POST | `/api/v1/cmdb/relationships` | Link CIs |
| GET | `/api/v1/cmdb/configuration-items/{id}/impact-analysis` | Impact analysis |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/dashboard/sla` | SLA metrics |
| GET | `/api/v1/reports/sla-breaches` | Breach report |
| GET | `/api/v1/analytics/mttr` | Mean Time To Resolve |

---

## 6. FILTER QUERY PARAMETERS

### Incidents
```
GET /api/v1/incidents?status=new,assigned&priority=critical,high&page=1&limit=20&sort_by=-priority,-sla_resolution_due&search=email

Parameters:
- status: new|assigned|in_progress|on_hold|resolved|closed|reopened
- priority: critical|high|medium|low
- assigned_to: {user_id}
- assigned_team: {team_id}
- sla_status: ON_TRACK|CRITICAL|BREACHED
- search: {text}
- date_from: 2026-01-01
- date_to: 2026-02-08
- page: {number}
- limit: {number}
- sort_by: created_at,-priority
```

### Service Requests
```
GET /api/v1/service-requests?status=pending_approval&service_id={id}&page=1

Parameters:
- status: submitted|pending_approval|approved|rejected|in_progress|completed|cancelled
- service_id: {uuid}
- requester: {user_id}
- page: {number}
```

---

## 7. WORKFLOW STATES & TRANSITIONS

### Incident Workflow
```
new 
  ↓
assigned 
  ↓
in_progress → on_hold ↘
  ↓                    → resolved
pending_user ←────────→
  ↓
closed
```

### Service Request Workflow
```
submitted
  ↓
pending_approval → approved
  ↓                  ↓
rejected ────→ in_progress
                  ↓
              completed/cancelled
```

### Change Workflow
```
draft
  ↓
submitted
  ↓
pending_approval
  ↓
approved → rejected
  ↓
in_progress
  ↓
completed → rolled_back
```

### Problem Workflow
```
new
  ↓
assigned
  ↓
investigating
  ↓
identified
  ↓
monitoring
  ↓
resolved
  ↓
closed
```

---

## 8. ROLE & PERMISSION MATRIX

| Action | End User | Agent | Manager | Admin |
|--------|----------|-------|---------|-------|
| Create Incident | ✓ | ✓ | ✓ | ✓ |
| View Own Tickets | ✓ | ✓ | ✓ | ✓ |
| View All Tickets | | ✓ | ✓ | ✓ |
| Update Ticket | | ✓ | ✓ | ✓ |
| Assign Ticket | | ✓ | ✓ | ✓ |
| Create Problem | | ✓ | ✓ | ✓ |
| Create Change | | ✓ | ✓ | ✓ |
| Approve Change | | | ✓ | ✓ |
| Manage Teams | | | ✓ | ✓ |
| Manage Users | | | | ✓ |
| Manage SLAs | | | | ✓ |
| View Reports | | ✓ | ✓ | ✓ |

---

## 9. ERROR CODES & RESPONSES

### Common Error Codes
```
400 Bad Request
  - VALIDATION_ERROR: Input validation failed
  - INVALID_STATE: Invalid state transition
  - DUPLICATE_TICKET: Ticket number already exists

401 Unauthorized
  - INVALID_TOKEN: JWT token invalid/expired
  - TOKEN_MISSING: Authorization header missing
  - MFA_REQUIRED: MFA verification required

403 Forbidden
  - INSUFFICIENT_PERMISSIONS: User lacks required permissions
  - NOT_ORGANIZATION_MEMBER: User not in organization
  - TICKET_LOCKED: Ticket being edited by another user

404 Not Found
  - RESOURCE_NOT_FOUND: Ticket/resource doesn't exist
  - ORGANIZATION_NOT_FOUND: Organization doesn't exist

409 Conflict
  - TICKET_NUMBER_EXISTS: Duplicate ticket number
  - INVALID_WORKFLOW_STATE: Cannot perform action in current state

429 Too Many Requests
  - RATE_LIMIT_EXCEEDED: API rate limit exceeded
  - RETRY_AFTER: Seconds to wait before retry

500 Internal Server Error
  - SERVER_ERROR: Unexpected server error
```

### Error Response Format
```json
{
  "success": false,
  "status_code": 400,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Input validation failed",
    "details": [
      {
        "field": "priority",
        "message": "Must be one of: critical, high, medium, low"
      }
    ]
  }
}
```

---

## 10. COMMON TASKS & HOW-TO

### Create & Assign Incident
```
1. POST /api/v1/incidents
   - title, description, category
   - impact, urgency (auto-calculates priority)
   
2. Backend auto-assigns based on:
   - Team workload
   - Agent skills
   - Availability
   
3. PUT /api/v1/incidents/{id}
   - assigned_to_id or assigned_to_team_id
```

### Multi-Level Approval
```
1. POST /api/v1/service-requests
2. System identifies approvers based on:
   - Service requirements
   - Cost threshold
   - User role
3. For each approval step:
   - POST /api/v1/service-requests/{id}/approve
   - or /api/v1/service-requests/{id}/reject
4. Move to next approver or complete
```

### Link Incident to Problem
```
Method 1: Automatic (system detects duplicates)
- Create incident with similar symptoms
- System automatically links to existing problem

Method 2: Manual
- POST /api/v1/incidents/{incident_id}
- Set problem_id field

Method 3: Via Problem
- Create problem
- POST /api/v1/problems/{problem_id}/link-incidents
- Provide incident IDs to link
```

### Calculate Impact Analysis
```
GET /api/v1/cmdb/configuration-items/{ci_id}/impact-analysis

Returns:
- Dependent CIs (what depends on this CI)
- Supporting CIs (what this CI depends on)
- Affected services
- Potential impact description
```

### Generate SLA Report
```
GET /api/v1/reports/sla-breaches?period=month&breach_type=resolution

Returns:
- Total breaches
- Breached tickets
- Breach duration
- By team breakdown
- Trends
```

---

## 11. IMPORTANT FILES & LOCATIONS

### Backend
```
/itsm-backend/
├── config/settings.py          # Configuration
├── apps/incidents/             # Incident module
├── apps/incidents/models.py    # Incident model
├── apps/incidents/views.py     # Incident API
├── apps/incidents/serializers.py # Data serialization
├── apps/incidents/services.py  # Business logic
└── tests/                       # Test files
```

### Frontend
```
/itsm-frontend/
├── src/pages/Incidents/        # Incident pages
├── src/components/Incident/    # Incident components
├── src/services/api.js         # API client
├── src/store/                  # Redux store
├── src/hooks/                  # Custom hooks
└── src/utils/                  # Utilities
```

### Database
```
PostgreSQL Database: itsm_db
Tables: 50+
Views: 10+
Triggers: 15+
Indexes: 30+
```

---

## 12. MONITORING & HEALTH CHECKS

### Health Check Endpoints
```
GET /api/v1/health                    # System health
GET /api/v1/health/database           # DB connection
GET /api/v1/health/redis              # Cache connection
GET /api/v1/health/elasticsearch      # Search engine
```

### Key Metrics to Monitor
```
Application:
- API response time (target: <200ms p95)
- Error rate (target: <0.1%)
- Request rate (peak load)
- Active users

Database:
- Query time (target: <100ms p95)
- Connection pool usage
- Slow queries
- Replication lag (if applicable)

Infrastructure:
- CPU usage (target: <80%)
- Memory usage (target: <85%)
- Disk usage (target: <90%)
- Network latency
```

### Alert Thresholds
```
High Priority (Immediate):
- Error rate > 1%
- API response time > 1 second
- Database unavailable
- Low disk space (<10%)

Medium Priority (Within 1 hour):
- Error rate > 0.5%
- API response time > 500ms
- SLA breach imminent
- High memory usage (>95%)

Low Priority (Daily review):
- Slow queries detected
- Unusual traffic patterns
- Backup status
```

---

## 13. TROUBLESHOOTING QUICK GUIDE

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| 401 Unauthorized | Invalid/expired token | Login again, check token expiration |
| 403 Forbidden | Insufficient permissions | Check user role and permissions |
| 500 Server Error | Bug in code | Check logs, contact dev team |
| Slow response | Database query | Optimize query, add index |
| SLA calculation wrong | Business hours config | Check SLA policy, verify business hours |
| Assignment not working | No available agents | Check team availability, workload |
| Email not sent | SMTP config | Check email service credentials |
| WebSocket timeout | Network/firewall | Check firewall rules, reconnect |

---

## 14. PERFORMANCE OPTIMIZATION TIPS

### Database
```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_incidents_priority ON incidents(priority);
CREATE INDEX idx_incidents_status ON incidents(status);

-- Use EXPLAIN to analyze slow queries
EXPLAIN ANALYZE SELECT * FROM incidents WHERE status = 'new';

-- Monitor slow query log
SET log_min_duration_statement = 100;  -- Log queries >100ms
```

### API
```python
# Use pagination
GET /api/v1/incidents?page=1&limit=50

# Use select_related for foreign keys
incidents = Incident.objects.select_related('assigned_to', 'team')

# Use prefetch_related for reverse relations
incidents = Incident.objects.prefetch_related('comments')

# Cache frequently accessed data
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def get_service_catalog(request):
    ...
```

### Frontend
```javascript
// Code splitting
const Incidents = lazy(() => import('./pages/Incidents'));

// Virtualization for large lists
import { FixedSizeList } from 'react-window';

// Memoization
const IncidentCard = React.memo(({ incident }) => {...});

// Debounce search
const searchIncidents = debounce((query) => {...}, 300);
```

---

## 15. SECURITY CHECKLISTS

### Before Going Live
- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Enable CSRF protection
- [ ] Set security headers (CSP, X-Frame-Options)
- [ ] Remove debug mode
- [ ] Configure email encryption
- [ ] Set up MFA
- [ ] Configure backup encryption
- [ ] Run security scan (OWASP ZAP, Burp)
- [ ] Conduct penetration test
- [ ] Review audit logs
- [ ] Test disaster recovery

### Regular Security Tasks
- [ ] Apply security patches (monthly)
- [ ] Rotate secrets/passwords (quarterly)
- [ ] Review access logs (weekly)
- [ ] Backup verification (weekly)
- [ ] DR drill (quarterly)
- [ ] Security training (annually)

---

## 16. USEFUL COMMANDS

### Database
```bash
# Backup
pg_dump -U itsm_user itsm_db > backup.sql

# Restore
psql -U itsm_user itsm_db < backup.sql

# Connect
psql -U itsm_user -d itsm_db

# List tables
\dt

# Describe table
\d incidents
```

### Django
```bash
# Migrate
python manage.py migrate

# Create migration
python manage.py makemigrations

# Run tests
pytest

# Create superuser
python manage.py createsuperuser

# Shell
python manage.py shell

# Collect static
python manage.py collectstatic
```

### Docker
```bash
# Start services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f app

# Run command in container
docker-compose exec app python manage.py migrate
```

---

## 17. CONTACT & SUPPORT

### Internal Support
- **Tech Lead**: [Email/Slack]
- **Database Admin**: [Email/Slack]
- **DevOps**: [Email/Slack]

### External Support
- **Cloud Provider**: [Contact info]
- **Database Support**: [Contact info]

### Escalation Path
1. Team member
2. Tech lead
3. Manager
4. Vendor (if applicable)

---

## 18. USEFUL LINKS

| Resource | URL |
|----------|-----|
| API Documentation | /api/v1/docs |
| Architecture Overview | [Link to docs] |
| Database Schema | [Link to docs] |
| Runbooks | [Link] |
| Incident Reports | [Link] |
| SLA Metrics | [Link] |

---

**Last Updated**: 2026-02-08  
**Document Version**: 1.0  
**Author**: Senior Architect  
**Next Review**: Monthly

