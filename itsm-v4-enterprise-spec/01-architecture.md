# 01. System Architecture

## Goals
- Enterprise scale (10,000+ users, multi-site, multi-department)
- API-first and microservices-ready
- ISO 20000-1 and ISO 27001 best practice alignment
- Strong security posture (OWASP, zero-trust-compatible)

## Logical Architecture

```mermaid
flowchart LR
  Users[End Users / Agents / Managers / Auditors] --> Web[Web App (React)]
  Web --> APIGW[API Gateway / BFF]
  APIGW --> IAM[Identity & Access Service]
  APIGW --> Ticket[Ticketing Service]
  APIGW --> Problem[Problem Service]
  APIGW --> Change[Change Enablement Service]
  APIGW --> CMDB[CMDB Service]
  APIGW --> Assets[Asset Service]
  APIGW --> Catalog[Service Catalog Service]
  APIGW --> Knowledge[Knowledge Service]
  APIGW --> SLA[SLA & Reporting Service]
  APIGW --> Workflow[Workflow Orchestration]
  APIGW --> Notify[Notification Service]
  APIGW --> Audit[Audit & Compliance Service]

  Ticket --> DB[(PostgreSQL Cluster)]
  Problem --> DB
  Change --> DB
  CMDB --> DB
  Assets --> DB
  Catalog --> DB
  Knowledge --> DB
  SLA --> DB
  Workflow --> DB
  Audit --> DB

  Ticket --> Cache[(Redis Cluster)]
  Workflow --> Queue[(Message Queue)]
  Notify --> Queue

  APIGW --> Search[(Search Index)]
  SLA --> Metrics[(Metrics/Observability)]
  Audit --> SIEM[(SIEM / Log Aggregator)]

  IAM --> SSO[SSO / IdP: Azure AD, LDAP, SAML, OAuth2]
```

## Deployment Topology (HA-ready)
- Stateless app services with horizontal scaling
- PostgreSQL with streaming replication and read replicas
- Redis with sentinel or managed cluster
- Queue broker (RabbitMQ or Redis Streams) for async workloads
- Object storage for attachments (S3-compatible)

## Non-Functional Requirements
- Availability: 99.9%+ (HA setup)
- RPO: 15 minutes, RTO: 4 hours
- Audit log immutability with hash chaining
- Mean response time < 500ms for core APIs

## Observability
- Structured logs (JSON)
- Metrics (Prometheus-compatible)
- Tracing (OpenTelemetry)
- Security audit events to SIEM
