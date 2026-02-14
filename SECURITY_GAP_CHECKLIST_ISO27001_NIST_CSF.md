# Security Gap Checklist - ISO 27001:2022 + NIST CSF 2.0

Date: 2026-02-14
Scope: Application-level controls and configuration hooks visible in this codebase.
Status legend: Implemented / Partial / Gap

## Summary
This checklist is a readiness map, not a certification. Formal ISO 27001 or NIST CSF compliance requires evidence collection, control testing, and audit.

## Combined Checklist

| Domain | Standard Mapping | Status | Evidence | Gaps / Actions |
| --- | --- | --- | --- | --- |
| Governance | CSF GV.* / ISO A.5 | Partial | Policy placeholders and compliance module docs in backend | Formal security policy, risk register, and roles/responsibilities evidence needed. |
| Asset Management | CSF ID.AM / ISO A.5, A.8 | Partial | CMDB module and assets UI | Define asset inventory coverage, ownership, and classification procedures. |
| Identity & Access | CSF PR.AC / ISO A.5, A.8 | Partial | JWT auth, RBAC roles, MFA endpoints | Enforce MFA for privileged roles; document access review process. |
| Authentication Hardening | CSF PR.AC / ISO A.5 | Implemented | Login lockout and password validation in auth endpoints | Add account recovery and admin notification on lockout. |
| Logging & Monitoring | CSF DE.CM / ISO A.8 | Partial | Request logging and security logger configured | Add centralized log forwarding and alerting thresholds. |
| Audit Logging | CSF GV, PR / ISO A.8 | Partial | AuditLog model + API viewset | Implement broader audit capture (CRUD events) and retention enforcement. |
| Data Protection | CSF PR.DS / ISO A.8 | Partial | TLS and secure cookie settings in production | Implement at-rest encryption per storage/database; manage keys. |
| Secure Configuration | CSF PR.IP / ISO A.5, A.8 | Partial | Production security settings; env flags | Ensure hardened defaults for production builds and infrastructure. |
| Vulnerability Management | CSF ID.RA / ISO A.8 | Gap | Not evident in codebase | Add scanning pipeline and remediation SLAs. |
| Incident Response | CSF RS.* / ISO A.5, A.8 | Partial | Incident module exists | Add security incident playbooks and evidence of exercises. |
| Backup & Recovery | CSF RC.* / ISO A.5, A.8 | Partial | Backup settings in env | Document and test backup/restore procedures; automate verification. |
| Business Continuity | CSF RC / ISO A.5 | Gap | Not evident in app docs | Add BCP/DR plans and test evidence. |
| Privacy | ISO A.5, A.8 | Gap | Not evident | Add data minimization, retention, and DPIA records. |
| Supplier Security | ISO A.5 | Gap | Not evident | Document third-party risk and supplier SLAs. |

## Notes
- This checklist focuses on application controls. Infrastructure controls (WAF, network segmentation, disk encryption, SIEM) must be addressed separately.
- If you want a formal audit pack, we can add control owners, evidence links, and test results.
