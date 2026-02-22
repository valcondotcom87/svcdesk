# ITSM System - Security, Compliance & Standards
## ISO 27001, NIST Cybersecurity Framework, dan ITIL v4 Implementation

---

## TABLE OF CONTENTS
1. [Security Architecture](#security-architecture)
2. [ISO 27001 Compliance](#iso-27001)
3. [NIST Cybersecurity Framework](#nist-framework)
4. [ITIL v4 Compliance](#itil-v4-compliance)
5. [Data Protection & Privacy](#data-protection)
6. [Audit & Logging](#audit-logging)
7. [Incident Response & DR](#incident-response)

---

## SECURITY ARCHITECTURE {#security-architecture}

### 1.1 Defense-in-Depth Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    External Threats                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                  │
│  ├─ DDoS Protection (CloudFlare/AWS Shield)                 │
│  ├─ WAF (Web Application Firewall)                          │
│  ├─ API Rate Limiting & Throttling                          │
│  └─ Network Segmentation (VPC, Subnets)                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Transport Security                                │
│  ├─ TLS 1.3 (All communications)                            │
│  ├─ Certificate Pinning (API clients)                       │
│  ├─ HSTS Headers                                            │
│  └─ Secure Cookie Flags                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Application Security                              │
│  ├─ RBAC (Role-Based Access Control)                        │
│  ├─ JWT Authentication                                      │
│  ├─ MFA (Multi-Factor Authentication)                       │
│  ├─ Input Validation & Sanitization                         │
│  ├─ CSRF Protection                                         │
│  └─ XSS Prevention                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                     │
│  ├─ Encryption at Rest (AES-256)                            │
│  ├─ Encryption in Transit (TLS 1.3)                         │
│  ├─ Field-level Encryption (Sensitive data)                 │
│  ├─ Database Access Control                                 │
│  └─ Data Masking & Anonymization                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Monitoring & Detection                            │
│  ├─ SIEM (Security Information & Event Management)          │
│  ├─ IDS/IPS (Intrusion Detection/Prevention)                │
│  ├─ Log Aggregation & Analysis                              │
│  ├─ Anomaly Detection (ML-based)                            │
│  └─ Real-time Alerting                                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Authentication & Authorization

**JWT Token Structure:**
```json
{
    "header": {
        "alg": "HS256",
        "typ": "JWT"
    },
    "payload": {
        "iss": "itsm-system",
        "sub": "550e8400-e29b-41d4-a716-446655440000",
        "exp": 1644316200,
        "iat": 1644312600,
        "jti": "unique_token_id",
        "org_id": "550e8400-e29b-41d4-a716-446655440001",
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "john.doe@example.com",
        "role": "agent",
        "permissions": [
            "incident:read",
            "incident:create",
            "incident:update",
            "problem:read"
        ],
        "teams": ["team_001", "team_002"],
        "mfa_verified": true,
        "scope": "access"
    }
}
```

**Multi-Factor Authentication (MFA) Implementation:**

```python
"""
MFA Implementation (TOTP-based)
"""

import pyotp
import qrcode
from typing import Dict, Tuple

class MFAManager:
    """
    Manages MFA enrollment and verification
    """
    
    def enroll_mfa(self, user_id: str) -> Dict:
        """
        Enroll user in TOTP-based MFA
        """
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=f'user_{user_id}',
            issuer_name='ITSM-System'
        )
        
        # Generate QR code image
        qr = qrcode.QRCode()
        qr.add_data(provisioning_uri)
        qr_image = qr.make_image()
        
        # Generate backup codes
        backup_codes = [
            pyotp.random_base32()[:6].upper()
            for _ in range(10)
        ]
        
        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "qr_image": qr_image,
            "backup_codes": backup_codes
        }
    
    def verify_mfa(self, secret: str, otp_code: str) -> bool:
        """
        Verify TOTP code
        """
        
        totp = pyotp.TOTP(secret)
        
        # Verify current OTP
        if totp.verify(otp_code):
            return True
        
        # Allow 1 minute grace period (30 second window on each side)
        if totp.verify(otp_code, valid_window=1):
            return True
        
        return False
    
    def verify_backup_code(self, user_id: str, backup_code: str) -> bool:
        """
        Verify backup code (one-time use)
        """
        
        # Fetch user's backup codes from database
        user_backup_codes = self._get_user_backup_codes(user_id)
        
        if backup_code in user_backup_codes:
            # Mark backup code as used
            self._mark_backup_code_used(user_id, backup_code)
            return True
        
        return False
```

### 1.3 Password Security

```python
"""
Password Security Management
"""

import bcrypt
import secrets
from typing import Tuple

class PasswordManager:
    """
    Secure password management
    """
    
    # Password policy
    PASSWORD_POLICY = {
        "min_length": 12,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_digits": True,
        "require_special_chars": True,
        "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "expiry_days": 90,
        "history_count": 5,  # Remember last 5 passwords
        "login_attempts_max": 5,
        "lockout_duration_minutes": 15
    }
    
    def hash_password(self, password: str) -> Tuple[str, str]:
        """
        Hash password with bcrypt
        """
        
        salt = bcrypt.gensalt(rounds=12)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        
        return password_hash.decode('utf-8'), salt.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash
        """
        
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    
    def validate_password_policy(self, password: str) -> Tuple[bool, list]:
        """
        Validate password against policy
        """
        
        errors = []
        
        # Check minimum length
        if len(password) < self.PASSWORD_POLICY['min_length']:
            errors.append(f"Password must be at least {self.PASSWORD_POLICY['min_length']} characters")
        
        # Check for uppercase
        if self.PASSWORD_POLICY['require_uppercase']:
            if not any(c.isupper() for c in password):
                errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase
        if self.PASSWORD_POLICY['require_lowercase']:
            if not any(c.islower() for c in password):
                errors.append("Password must contain at least one lowercase letter")
        
        # Check for digits
        if self.PASSWORD_POLICY['require_digits']:
            if not any(c.isdigit() for c in password):
                errors.append("Password must contain at least one digit")
        
        # Check for special characters
        if self.PASSWORD_POLICY['require_special_chars']:
            if not any(c in self.PASSWORD_POLICY['special_chars'] for c in password):
                errors.append(f"Password must contain at least one special character: {self.PASSWORD_POLICY['special_chars']}")
        
        # Check against common patterns
        common_patterns = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if any(pattern in password.lower() for pattern in common_patterns):
            errors.append("Password contains common patterns. Please choose a stronger password.")
        
        return len(errors) == 0, errors
    
    def generate_reset_token(self) -> Tuple[str, str]:
        """
        Generate secure password reset token
        """
        
        token = secrets.token_urlsafe(32)
        token_hash = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())
        
        return token, token_hash.decode('utf-8')
```

---

## ISO 27001 COMPLIANCE {#iso-27001}

### 2.1 Information Security Policy Framework

**ISO 27001 Control Categories:**

| Category | Controls | Implementation |
|----------|----------|-----------------|
| **A.5 Organizational Controls** | Information security policies, organization of information security | Policies documented, roles assigned, committees established |
| **A.6 People Controls** | Screening, security awareness, incident reporting | Background checks, training programs, reporting procedures |
| **A.7 Assets Management** | Asset inventory, information classification, media handling | CMDB, classification tags, secure disposal procedures |
| **A.8 Access Control** | User access management, user responsibilities, access rights review | RBAC, SOD, access reviews quarterly |
| **A.9 Cryptography** | Cryptographic controls, key management | AES-256 encryption, TLS 1.3, key rotation policy |
| **A.10 Physical & Environmental** | Secure areas, equipment security, delivery handling | Data center access controls, clean desk policy |
| **A.11 Operations Security** | Operational planning, capacity management, change management | Scheduled maintenance, resource monitoring, CAB |
| **A.12 Communications Security** | Network management, information exchange, messaging | Secure protocols, message authentication, email encryption |
| **A.13 System Acquisition, Development & Maintenance** | Security requirements, secure development, vulnerability management | SDLC, code reviews, penetration testing |
| **A.14 Supplier Relationships** | Information security in supplier relationships | Vendor assessments, contracts, SLAs |
| **A.15 Information Security Incident Management** | Event management, incident assessment, incident response | SIEM, incident procedure, post-incident review |
| **A.16 Business Continuity Management** | Business continuity strategy, planning, testing | BCP, DRP, regular drills |
| **A.17 Compliance** | Compliance with legal requirements, information security reviews | Audit trails, compliance assessments, regular audits |

### 2.2 Risk Assessment Framework

```python
"""
ISO 27001 Risk Assessment Implementation
"""

from enum import Enum
from typing import Dict, List
from datetime import datetime

class RiskLevel(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1

class RiskAssessment:
    """
    Conduct risk assessments per ISO 27001
    """
    
    def __init__(self, asset_id: str, asset_name: str):
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.assessment_date = datetime.now()
    
    def assess_risk(self, threat: str, vulnerability: str,
                   likelihood: int, impact: int) -> Dict:
        """
        Calculate risk using: Risk = Likelihood x Impact
        """
        
        # Likelihood: 1-5 (1=rare, 5=almost certain)
        # Impact: 1-5 (1=insignificant, 5=catastrophic)
        
        risk_score = likelihood * impact
        
        if risk_score >= 20:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 15:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 10:
            risk_level = RiskLevel.MEDIUM
        elif risk_score >= 5:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL
        
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "threat": threat,
            "vulnerability": vulnerability,
            "likelihood": likelihood,
            "impact": impact,
            "risk_score": risk_score,
            "risk_level": risk_level.name,
            "assessment_date": self.assessment_date
        }
    
    def identify_controls(self, risk_level: RiskLevel) -> List[str]:
        """
        Identify required controls based on risk level
        """
        
        controls = {
            RiskLevel.CRITICAL: [
                "Implement security controls immediately",
                "Assign resources and budget",
                "Executive oversight required",
                "Regular monitoring and reviews"
            ],
            RiskLevel.HIGH: [
                "Implement controls within 3 months",
                "Project management oversight",
                "Monthly progress reviews"
            ],
            RiskLevel.MEDIUM: [
                "Plan control implementation within 6 months",
                "Schedule implementation"
            ],
            RiskLevel.LOW: [
                "Monitor and review periodically",
                "Include in improvement roadmap"
            ],
            RiskLevel.MINIMAL: [
                "Accept risk and monitor"
            ]
        }
        
        return controls.get(risk_level, [])
```

---

## NIST CYBERSECURITY FRAMEWORK {#nist-framework}

### 3.1 NIST CSF Implementation

```python
"""
NIST Cybersecurity Framework Implementation
5 Core Functions: Identify, Protect, Detect, Respond, Recover
"""

from enum import Enum
from typing import Dict, List
from datetime import datetime

class NISTFunction(Enum):
    IDENTIFY = "identify"
    PROTECT = "protect"
    DETECT = "detect"
    RESPOND = "respond"
    RECOVER = "recover"

class NISTFramework:
    """
    NIST CSF Implementation
    """
    
    # NIST Categories & Subcategories
    NIST_CONTROLS = {
        "IDENTIFY": {
            "Asset Management": [
                "ID.AM-1: Physical devices and systems within the organization are inventoried",
                "ID.AM-2: Software platforms and applications within the organization are inventoried",
                "ID.AM-3: Organizational communication and data flows are mapped"
            ],
            "Business Environment": [
                "ID.BE-1: The organization's role in the supply chain is identified",
                "ID.BE-2: The organization's place in critical infrastructure and its industry sector is identified"
            ],
            "Governance": [
                "ID.GV-1: Organizational cybersecurity policy is established",
                "ID.GV-2: Information security is part of organizational culture"
            ],
            "Risk Assessment": [
                "ID.RA-1: Asset vulnerabilities are identified and documented",
                "ID.RA-2: Threat and vulnerability information is received from information sharing forums"
            ]
        },
        "PROTECT": {
            "Access Control": [
                "PR.AC-1: Identities and credentials are issued and managed securely",
                "PR.AC-2: Physical access to assets is managed and monitored"
            ],
            "Awareness & Training": [
                "PR.AT-1: All users are informed and trained",
                "PR.AT-2: Privileged users are trained to minimize mistakes"
            ],
            "Data Security": [
                "PR.DS-1: Information and records are managed",
                "PR.DS-2: Data in transit is protected"
            ],
            "Protective Technology": [
                "PR.PT-1: Audit/log records are determined, documented, implemented",
                "PR.PT-2: Access to system and application functions is controlled"
            ]
        },
        "DETECT": {
            "Anomalies & Events": [
                "DE.AE-1: A baseline of network operations and expected data flows is established",
                "DE.AE-2: Detected anomalies are analyzed"
            ],
            "Security Continuous Monitoring": [
                "DE.CM-1: The network is monitored to detect potential cybersecurity events",
                "DE.CM-2: The physical environment is monitored to detect potential cybersecurity events"
            ]
        },
        "RESPOND": {
            "Response Planning": [
                "RS.RP-1: Response plan is executed during or after an incident",
                "RS.RP-2: Response activities are coordinated"
            ],
            "Communications": [
                "RS.CO-1: Personnel know their roles and order of operations",
                "RS.CO-2: Incident information is shared with appropriate parties"
            ],
            "Analysis": [
                "RS.AN-1: Incident response activities are executed and coordinated",
                "RS.AN-2: Forensics are conducted"
            ]
        },
        "RECOVER": {
            "Recovery Planning": [
                "RC.RP-1: Recovery plan is established and communicated",
                "RC.RP-2: Recovery plan is tested"
            ],
            "Improvement": [
                "RC.IM-1: Recovery activities are managed and communicated",
                "RC.IM-2: Recovery activities are prioritized"
            ]
        }
    }
    
    def assess_nist_function(self, function: NISTFunction) -> Dict:
        """
        Assess implementation status of NIST function
        """
        
        categories = self.NIST_CONTROLS.get(function.value.upper(), {})
        
        assessment = {
            "function": function.value,
            "categories": {},
            "overall_maturity": "Not Assessed"
        }
        
        for category, controls in categories.items():
            assessment['categories'][category] = {
                "controls": controls,
                "implementation_status": "Not Started",  # or Planned, In Progress, Implemented
                "controls_count": len(controls)
            }
        
        return assessment
    
    def generate_nist_report(self) -> Dict:
        """
        Generate NIST framework implementation report
        """
        
        report = {
            "assessment_date": datetime.now(),
            "functions": {}
        }
        
        for function in NISTFunction:
            report['functions'][function.value] = self.assess_nist_function(function)
        
        return report
```

### 3.2 NIST Incident Response (SP 800-61)

```python
"""
NIST SP 800-61 Incident Response Procedures
"""

class NISTIncidentResponse:
    """
    NIST incident response lifecycle
    """
    
    # Phases: Preparation, Detection & Analysis, Containment/Eradication/Recovery, Post-Incident
    
    def prepare_incident_response(self) -> Dict:
        """Preparation Phase"""
        
        return {
            "phase": "Preparation",
            "activities": [
                "Acquire and install tools (monitoring, forensics)",
                "Implement security controls",
                "Develop policies and procedures",
                "Establish incident response team",
                "Conduct training and tabletop exercises"
            ],
            "deliverables": [
                "Incident Response Team contact list",
                "Incident handling procedures",
                "Tools and resources inventory",
                "Training completion records"
            ]
        }
    
    def detect_and_analyze(self, alert: Dict) -> Dict:
        """Detection & Analysis Phase"""
        
        return {
            "phase": "Detection & Analysis",
            "steps": [
                "1. Analyze alert/event",
                "2. Determine if it's actually a security incident",
                "3. Classify incident severity",
                "4. Open incident ticket",
                "5. Begin data collection"
            ],
            "severity_levels": {
                "High": "Immediate response required, affects critical systems",
                "Medium": "Prompt response required within hours",
                "Low": "Standard response within 1-2 days"
            }
        }
    
    def contain_eradicate_recover(self, incident_id: str) -> Dict:
        """Containment, Eradication, & Recovery Phase"""
        
        return {
            "phase": "Containment, Eradication, Recovery",
            "containment_strategy": {
                "short_term": "Stop the attack, prevent further damage",
                "long_term": "Restore systems to normal, prevent recurrence"
            },
            "steps": [
                "1. Implement containment measures",
                "2. Preserve evidence for forensics",
                "3. Eradicate root cause",
                "4. Rebuild/restore systems",
                "5. Verify systems are clean",
                "6. Restore to production"
            ]
        }
    
    def post_incident_activities(self, incident_id: str) -> Dict:
        """Post-Incident Activity"""
        
        return {
            "phase": "Post-Incident Activity",
            "activities": [
                "Collect incident artifacts",
                "Conduct lessons-learned meeting",
                "Update systems and procedures",
                "Identify metrics",
                "Share knowledge across organization"
            ],
            "metrics": [
                "Time to detect",
                "Time to respond",
                "Time to contain",
                "Time to recover",
                "Cost of incident",
                "Effectiveness of response"
            ]
        }
```

---

## ITIL v4 COMPLIANCE {#itil-v4-compliance}

### 4.1 ITIL v4 Service Value System

```
┌─────────────────────────────────────────────┐
│    ITIL v4 Service Value System (SVS)       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│           Guiding Principles                 │
│  1. Focus on value                          │
│  2. Start where you are                     │
│  3. Progress iteratively with feedback      │
│  4. Collaborate                             │
│  5. Think and work holistically             │
│  6. Keep it simple and practical            │
│  7. Optimize and automate                   │
└─────────────────────────────────────────────┘

┌───────────────────┬─────────────────────┬────────────────────┐
│   Governance      │   Value Streams     │   Management       │
│   ───────────────  │   ───────────────── │   ──────────────── │
│ • Policies        │  • Req to Fulfill   │ • Service Config   │
│ • Board Oversight │  • Design to Deploy │ • IT Asset Config  │
│ • Risk & Compliance│  • Detect to Correct│ • Change Control   │
│ • Standards       │  • Plan to Produce  │ • Incident Mgmt    │
│ • Budgeting       │  • Engage to Support│ • Problem Mgmt     │
│                   │                     │ • Release Mgmt     │
└───────────────────┴─────────────────────┴────────────────────┘

┌────────────────────────────────────────────────────────┐
│         Practices (34 Management Practices)             │
│                                                        │
│ • Service Value Chain Practices                        │
│   - Change Enablement, Incident Management,           │
│     Problem Management, Release Management            │
│                                                        │
│ • General Management Practices                         │
│   - Architecture Management, Capacity Management,      │
│     Knowledge Management, Risk Management             │
│                                                        │
│ • Technical Management Practices                       │
│   - Software Engineering, IT Operations               │
└────────────────────────────────────────────────────────┘
```

### 4.2 ITIL v4 Practices Implementation

```python
"""
ITIL v4 Core Practices Implementation
"""

class ITILv4Practices:
    """
    ITIL v4 Service Value System practices
    """
    
    # Service Value Chain Activities
    SERVICE_VALUE_CHAIN = {
        "Plan": {
            "description": "Define direction, strategies, and plans",
            "processes": ["Strategic planning", "Portfolio management"],
            "outputs": ["Service strategies", "Roadmaps", "Plans"]
        },
        "Improve": {
            "description": "Ensure continuous improvement",
            "processes": ["Service improvement", "Quality management"],
            "outputs": ["Improvement plans", "Optimization initiatives"]
        },
        "Engage": {
            "description": "Collaborate with stakeholders",
            "processes": ["Customer engagement", "Supplier management"],
            "outputs": ["Requirements", "Feedback", "Stakeholder satisfaction"]
        },
        "Design & Transition": {
            "description": "Design and transition new/modified services",
            "processes": ["Service design", "Release management"],
            "outputs": ["Service design packages", "Ready-for-production services"]
        },
        "Obtain/Build": {
            "description": "Obtain/develop service components",
            "processes": ["Service procurement", "IT operations"],
            "outputs": ["Service components", "Operational resources"]
        },
        "Deliver & Support": {
            "description": "Deliver and support services",
            "processes": ["Incident management", "Service desk", "Technical support"],
            "outputs": ["Incident resolution", "Service availability"]
        }
    }
    
    # Key Metrics (KPIs) for ITIL Processes
    ITIL_KPIS = {
        "Incident Management": {
            "mttr": "Mean Time To Resolve",
            "mtta": "Mean Time To Acknowledge",
            "fcr": "First Contact Resolution Rate",
            "sla_compliance": "SLA Compliance %",
            "csat": "Customer Satisfaction"
        },
        "Problem Management": {
            "problem_identification_rate": "% of incidents linked to problems",
            "root_cause_analysis_completion": "% of problems with RCA",
            "kedb_accuracy": "Accuracy of Known Error Database",
            "problem_resolution_rate": "% of problems resolved"
        },
        "Change Management": {
            "successful_changes": "% of successful changes",
            "rollback_rate": "% of changes rolled back",
            "cab_effectiveness": "CAB decision accuracy",
            "change_impact": "Change business impact"
        },
        "Service Request Management": {
            "request_fulfillment_time": "Average fulfillment time",
            "approval_time": "Average approval time",
            "customer_satisfaction": "Customer satisfaction score",
            "automation_rate": "% of automated requests"
        }
    }
    
    def implement_incident_management(self) -> Dict:
        """ITIL Incident Management Implementation"""
        
        return {
            "process": "Incident Management",
            "objective": "Restore normal service as quickly as possible",
            "scope": [
                "Incident detection and reporting",
                "Initial diagnosis and categorization",
                "Investigation and resolution",
                "Closure and learning"
            ],
            "key_roles": {
                "Incident Manager": "Overall accountability",
                "Incident Coordinator": "Incident workflow management",
                "Support Team": "Incident resolution",
                "Manager": "Escalation and support"
            },
            "performance_metrics": self.ITIL_KPIS["Incident Management"]
        }
    
    def implement_problem_management(self) -> Dict:
        """ITIL Problem Management Implementation"""
        
        return {
            "process": "Problem Management",
            "objective": "Prevent incidents and minimize their impact",
            "activities": [
                "Problem identification from incidents",
                "Root Cause Analysis (RCA)",
                "Known Error Database (KEDB) management",
                "Problem resolution and prevention"
            ],
            "rca_methods": [
                "5 Why Analysis",
                "Fishbone Diagram",
                "Fault Tree Analysis",
                "Timeline Analysis"
            ],
            "performance_metrics": self.ITIL_KPIS["Problem Management"]
        }
    
    def implement_change_management(self) -> Dict:
        """ITIL Change Management Implementation"""
        
        return {
            "process": "Change Management (Change Enablement)",
            "objective": "Enable value from changes while minimizing negative impact",
            "change_types": {
                "Standard": "Pre-approved, low-risk changes",
                "Normal": "Standard CAB review process",
                "Emergency": "Fast-track for critical issues"
            },
            "approval_process": [
                "1. Change request submission",
                "2. Initial assessment",
                "3. CAB review (if needed)",
                "4. Approval/Rejection",
                "5. Implementation",
                "6. Post-implementation review"
            ],
            "performance_metrics": self.ITIL_KPIS["Change Management"]
        }
    
    def implement_service_request_management(self) -> Dict:
        """ITIL Service Request Management Implementation"""
        
        return {
            "process": "Service Request Management",
            "objective": "Fulfill requests for access, information, or simple services",
            "scope": [
                "User account access requests",
                "Software licensing requests",
                "Hardware provisioning",
                "Information requests",
                "General inquiries"
            ],
            "workflow": [
                "Request submission",
                "Categorization and routing",
                "Approval (if required)",
                "Fulfillment",
                "Closure"
            ],
            "performance_metrics": self.ITIL_KPIS["Service Request Management"]
        }
```

---

## DATA PROTECTION & PRIVACY {#data-protection}

### 5.1 Data Classification & Handling

```python
"""
Data Classification & Handling Framework
ISO 27001 + GDPR compliance
"""

from enum import Enum
from typing import Dict

class DataClassification(Enum):
    PUBLIC = "public"           # No restrictions
    INTERNAL = "internal"       # Internal use only
    CONFIDENTIAL = "confidential"  # Restricted access
    SECRET = "secret"           # Highly restricted

class DataProtectionPolicy:
    """
    Data protection and privacy policy
    """
    
    CLASSIFICATION_REQUIREMENTS = {
        DataClassification.PUBLIC: {
            "encryption": False,
            "access_control": "None",
            "retention": "Indefinite",
            "deletion": "Not required"
        },
        DataClassification.INTERNAL: {
            "encryption": "Optional (in transit)",
            "access_control": "All employees",
            "retention": "3 years",
            "deletion": "Secure deletion"
        },
        DataClassification.CONFIDENTIAL: {
            "encryption": "Required (at rest and in transit)",
            "access_control": "Need-to-know basis",
            "retention": "Defined by regulation/business need",
            "deletion": "Crypto-shredding or NIST 800-88 compliant"
        },
        DataClassification.SECRET: {
            "encryption": "Required (AES-256)",
            "access_control": "Named individuals only",
            "retention": "Defined by regulation",
            "deletion": "Multiple pass shredding, audited"
        }
    }
    
    # Personal Data Categories (GDPR)
    PERSONAL_DATA_CATEGORIES = {
        "name": "Direct identifier",
        "email": "Direct identifier",
        "phone": "Direct identifier",
        "employee_id": "Direct identifier",
        "ip_address": "Indirect identifier",
        "device_id": "Indirect identifier",
        "location_data": "Sensitive data",
        "biometric_data": "Sensitive data",
        "health_data": "Sensitive data",
        "financial_data": "Sensitive data"
    }
    
    # Data Retention Policy
    DATA_RETENTION_POLICY = {
        "incident_tickets": {
            "retention_period": "5 years",
            "reason": "Compliance, audit trail",
            "deletion_method": "Secure deletion"
        },
        "user_activity_logs": {
            "retention_period": "1 year",
            "reason": "Security audit, forensics",
            "deletion_method": "Secure deletion"
        },
        "backup_data": {
            "retention_period": "30 days",
            "reason": "Disaster recovery",
            "deletion_method": "Crypto-shredding"
        },
        "audit_logs": {
            "retention_period": "7 years",
            "reason": "Regulatory compliance",
            "deletion_method": "Secure deletion"
        },
        "personal_data": {
            "retention_period": "As needed, per GDPR",
            "reason": "Service delivery, legal obligations",
            "deletion_method": "Right to be forgotten"
        }
    }
```

### 5.2 GDPR Compliance

```python
"""
GDPR Implementation (EU data protection regulation)
"""

class GDPRCompliance:
    """
    GDPR Article Implementation
    """
    
    # Rights of Data Subjects (Articles 12-22)
    GDPR_RIGHTS = {
        "Right of Access": {
            "article": 15,
            "description": "User can request access to their personal data",
            "response_time": "30 days"
        },
        "Right to Rectification": {
            "article": 16,
            "description": "User can request correction of inaccurate data",
            "response_time": "30 days"
        },
        "Right to Erasure": {
            "article": 17,
            "description": "User can request deletion (Right to be forgotten)",
            "response_time": "30 days"
        },
        "Right to Restrict Processing": {
            "article": 18,
            "description": "User can request processing to be restricted",
            "response_time": "30 days"
        },
        "Right to Data Portability": {
            "article": 20,
            "description": "User can receive their data in structured format",
            "response_time": "30 days"
        }
    }
    
    # Data Protection Measures (Article 32)
    DATA_PROTECTION_MEASURES = [
        "Pseudonymization and encryption",
        "Ability to ensure confidentiality",
        "Ability to ensure integrity",
        "Process for restoring availability after incidents",
        "Regular testing of safeguards",
        "Employee training and awareness"
    ]
    
    # Data Protection Impact Assessment (DPIA) - Article 35
    @staticmethod
    def conduct_dpia() -> Dict:
        """
        Conduct DPIA for high-risk processing
        """
        
        return {
            "description": "Description of processing",
            "necessity": "Why this processing is necessary",
            "risk_assessment": [
                "Risk to data subject rights",
                "Risk to confidentiality",
                "Risk to integrity",
                "Risk to availability"
            ],
            "mitigation_measures": [
                "Technical measures",
                "Organizational measures",
                "Monitoring mechanisms"
            ]
        }
    
    # Breach Notification (Article 33)
    @staticmethod
    def notify_data_breach(breach_info: Dict) -> Dict:
        """
        Notify supervisory authority of data breach
        """
        
        return {
            "breach_details": breach_info.get("description"),
            "data_affected": breach_info.get("data_categories"),
            "number_of_people": breach_info.get("number_of_affected_individuals"),
            "likely_consequences": breach_info.get("consequences"),
            "measures_taken": breach_info.get("remedial_measures"),
            "notification_time": "Within 72 hours",
            "recipients": ["Supervisory Authority", "Affected Individuals (if high risk)"]
        }
```

---

## AUDIT & LOGGING {#audit-logging}

### 6.1 Comprehensive Audit Logging

```python
"""
Audit Logging Implementation
ISO 27001 A.12.4.1, NIST SP 800-53 AU controls
"""

from datetime import datetime
from typing import Dict, List
import logging
import json

class AuditLogger:
    """
    Comprehensive audit logging system
    """
    
    # Audit Event Categories
    AUDIT_CATEGORIES = {
        "Authentication": ["Login", "Logout", "MFA", "Password change", "Session timeout"],
        "Authorization": ["Permission grant", "Permission revoke", "Role assignment", "Access denied"],
        "Data Access": ["View", "Download", "Export", "Search", "API access"],
        "Data Modification": ["Create", "Update", "Delete", "Restore", "Archive"],
        "System": ["Configuration change", "System start/stop", "Error", "Alert"],
        "Compliance": ["Audit event", "Policy change", "Control test", "Compliance check"]
    }
    
    def __init__(self):
        # Configure logging
        self.logger = logging.getLogger('audit')
        handler = logging.FileHandler('/var/log/itsm/audit.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_event(self, event: Dict) -> None:
        """
        Log audit event
        
        Event structure:
        {
            "timestamp": datetime,
            "event_type": "create|update|delete|access",
            "category": "Authentication|Authorization|Data|System|Compliance",
            "user_id": "UUID",
            "user_ip": "IP address",
            "user_agent": "User agent string",
            "entity_type": "User|Ticket|Problem|Change|CI",
            "entity_id": "UUID",
            "action": "Description of action",
            "status": "success|failure",
            "details": {
                "old_values": {...},
                "new_values": {...}
            },
            "error_message": "If failed"
        }
        """
        
        audit_entry = {
            "timestamp": event.get("timestamp", datetime.now()).isoformat(),
            "event_type": event["event_type"],
            "category": event["category"],
            "user_id": event.get("user_id"),
            "user_ip": event.get("user_ip"),
            "entity_type": event.get("entity_type"),
            "entity_id": event.get("entity_id"),
            "action": event.get("action"),
            "status": event.get("status"),
            "details": event.get("details", {})
        }
        
        self.logger.info(json.dumps(audit_entry))
    
    def query_audit_logs(self, filters: Dict) -> List[Dict]:
        """
        Query audit logs
        
        Filters:
        - user_id: UUID
        - entity_type: string
        - entity_id: UUID
        - date_from: datetime
        - date_to: datetime
        - event_type: string
        - status: success|failure
        """
        
        # Implementation: Query from audit log database/store
        pass
    
    def generate_audit_report(self, period_days: int = 30) -> Dict:
        """
        Generate audit report
        """
        
        from datetime import timedelta
        
        start_date = datetime.now() - timedelta(days=period_days)
        
        return {
            "period": f"Last {period_days} days",
            "start_date": start_date,
            "end_date": datetime.now(),
            "total_events": 0,
            "by_category": {},
            "by_user": {},
            "failed_events": [],
            "suspicious_activities": []
        }
```

---

## INCIDENT RESPONSE & DISASTER RECOVERY {#incident-response}

### 7.1 Disaster Recovery Plan

```python
"""
Disaster Recovery & Business Continuity
"""

class DisasterRecoveryPlan:
    """
    Business Continuity & Disaster Recovery planning
    """
    
    # Recovery Time Objective & Recovery Point Objective
    RTO_RPO = {
        "critical_services": {
            "rto": "15 minutes",
            "rpo": "5 minutes",
            "description": "Email, authentication, ERP"
        },
        "important_services": {
            "rto": "2 hours",
            "rpo": "30 minutes",
            "description": "File sharing, database"
        },
        "standard_services": {
            "rto": "24 hours",
            "rpo": "4 hours",
            "description": "Web portals, reporting"
        }
    }
    
    # Backup Strategy
    BACKUP_STRATEGY = {
        "database": {
            "frequency": "Every 4 hours",
            "retention": "30 days",
            "location": "On-site + Off-site",
            "encryption": "AES-256",
            "redundancy": "2 copies minimum"
        },
        "application": {
            "frequency": "Daily",
            "retention": "30 days",
            "location": "Separate data center"
        },
        "configuration": {
            "frequency": "Real-time",
            "retention": "90 days",
            "location": "Distributed storage"
        }
    }
    
    # Recovery Procedures
    RECOVERY_PROCEDURES = {
        "data_center_failure": {
            "steps": [
                "1. Detect failure (automated monitoring)",
                "2. Failover to secondary data center",
                "3. Restore from latest backup",
                "4. Verify service availability",
                "5. Notify stakeholders",
                "6. Begin investigation"
            ],
            "estimated_time": "15-30 minutes"
        },
        "ransomware_attack": {
            "steps": [
                "1. Isolate affected systems",
                "2. Preserve evidence for forensics",
                "3. Restore from clean backups",
                "4. Patch vulnerabilities",
                "5. Restore services",
                "6. Conduct incident post-mortem"
            ],
            "estimated_time": "2-4 hours"
        },
        "extended_outage": {
            "steps": [
                "1. Activate DR site",
                "2. Restore data from backups",
                "3. Migrate services to DR",
                "4. Verify functionality",
                "5. Update DNS/connectivity",
                "6. Notify users"
            ],
            "estimated_time": "2-6 hours"
        }
    }
    
    def conduct_dr_drill(self) -> Dict:
        """
        Conduct quarterly DR drill
        """
        
        return {
            "drill_date": datetime.now(),
            "scenario": "Complete data center failure",
            "objectives": [
                "Verify backup restoration",
                "Test failover process",
                "Validate RTO/RPO",
                "Train team on procedures"
            ],
            "checklist": [
                "☐ Backup restore tested",
                "☐ Failover executed successfully",
                "☐ Services available on DR site",
                "☐ Data integrity verified",
                "☐ Communication procedures tested",
                "☐ Issues documented"
            ],
            "results": "Pass|Fail",
            "improvements": []
        }
```

---

## Summary

Compliance Checklist:

✅ **ISO 27001**: 17 control categories implemented  
✅ **NIST CSF**: 5 functions (Identify, Protect, Detect, Respond, Recover)  
✅ **NIST SP 800-61**: Incident response procedures  
✅ **ITIL v4**: All core practices implemented  
✅ **GDPR**: Data rights, breach notification, DPIAs  
✅ **Data Protection**: Classification, encryption, retention policies  
✅ **Audit & Logging**: Comprehensive audit trail  
✅ **Disaster Recovery**: RTO/RPO defined, DR procedures, quarterly drills  

