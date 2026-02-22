# 03. Workflow Diagrams (ITIL v4 Practices)

## Incident Management
```mermaid
flowchart TD
  A[New Incident] --> B[Classify Impact/Urgency]
  B --> C[Auto Priority]
  C --> D[Assign / Queue]
  D --> E[Investigate]
  E --> F[Resolve]
  F --> G[User Confirmation]
  G --> H[Close]
  D --> I[Major Incident?]
  I -->|Yes| J[Major Incident Process]
  J --> F
```

## Service Request Management
```mermaid
flowchart TD
  A[Request Submitted] --> B[Validate Request]
  B --> C{Approval Required?}
  C -->|Yes| D[Multi-level Approval]
  C -->|No| E[Auto Fulfillment]
  D --> E
  E --> F[User Confirmation]
  F --> G[Close]
```

## Problem Management
```mermaid
flowchart TD
  A[Problem Created] --> B[Classify & Prioritize]
  B --> C[Root Cause Analysis]
  C --> D[Known Error?]
  D -->|Yes| E[Publish Workaround]
  D -->|No| F[Create Fix]
  F --> G[Problem Resolved]
```

## Change Enablement
```mermaid
flowchart TD
  A[Change Raised] --> B[Categorize Type]
  B --> C[Risk Scoring]
  C --> D{Standard?}
  D -->|Yes| E[Pre-Approved]
  D -->|No| F[CAB Review]
  F --> G[Approve/Reject]
  G --> H[Schedule]
  H --> I[Implement]
  I --> J[Post-Implementation Review]
```

## Service Level Management
```mermaid
flowchart TD
  A[Ticket Created] --> B[Attach SLA Policy]
  B --> C[SLA Timer Running]
  C --> D{Breach Imminent?}
  D -->|Yes| E[Escalation]
  D -->|No| F[Continue]
  E --> F
  F --> G[Resolved]
  G --> H[Stop Timer + Report]
```

## Knowledge Management
```mermaid
flowchart TD
  A[Draft Article] --> B[Peer Review]
  B --> C[Approval]
  C --> D[Publish]
  D --> E[Review Cycle]
```

## CMDB & Asset Management
```mermaid
flowchart TD
  A[CI Created/Discovered] --> B[Validate]
  B --> C[Relationship Mapping]
  C --> D[Lifecycle Updates]
  D --> E[Retire]
```
