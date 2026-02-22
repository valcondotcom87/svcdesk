# Hardening Checklist

## Zero Trust and Identity
- Enforce MFA for all privileged and admin roles.
- SSO via Azure AD, Google, LDAP, or SAML.
- RBAC per module and per action.
- Session timeout and re-authentication for high-risk actions.

## Network and Perimeter
- Reverse proxy hardened (Nginx) with strong TLS ciphers.
- WAF enabled (Cloudflare or ModSecurity).
- API rate limiting and IP throttling.
- Network segmentation: DMZ, app, data tiers.

## Application Security
- Input validation and output encoding (OWASP).
- Secure file upload scanning and size limits.
- Immutable audit log with hash chaining.
- Audit events exported to SIEM.

## Data Protection
- Encryption at rest (DB + object storage).
- Encryption in transit (TLS 1.2+).
- Tenant data isolation enforced (schema-per-tenant).
- Data retention and legal hold policy.

## Operations
- Vulnerability scanning monthly.
- Patch management and OS hardening (CIS benchmarks).
- Backup encryption and immutability.
- DR drills and incident response playbooks.
