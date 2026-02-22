# 02. ERD (Entity Relationship Design)

```mermaid
erDiagram
  ORGANIZATION ||--o{ DEPARTMENT : has
  ORGANIZATION ||--o{ SITE : has
  ORGANIZATION ||--o{ TEAM : has
  USER ||--o{ USER_ROLE : assigned
  ROLE ||--o{ USER_ROLE : contains
  USER ||--o{ AUDIT_LOG : produces

  SERVICE_CATALOG ||--o{ SERVICE : offers
  SERVICE ||--o{ SERVICE_REQUEST : requested_by
  SERVICE_REQUEST ||--o{ APPROVAL : requires

  INCIDENT ||--o{ INCIDENT_COMMENT : has
  INCIDENT ||--o{ INCIDENT_LINK : relates
  INCIDENT ||--o{ PROBLEM : linked

  PROBLEM ||--o{ ROOT_CAUSE : includes
  PROBLEM ||--o{ KNOWN_ERROR : results

  CHANGE ||--o{ CHANGE_APPROVAL : has
  CHANGE ||--o{ CHANGE_CALENDAR : scheduled
  CHANGE ||--o{ RISK_ASSESSMENT : evaluated

  CI ||--o{ CI_RELATIONSHIP : depends
  CI ||--o{ INCIDENT : linked
  CI ||--o{ CHANGE : impacted
  CI ||--o{ ASSET : mapped

  ASSET ||--o{ ASSET_LIFECYCLE : tracks
  ASSET ||--o{ CONTRACT : covered

  SLA_POLICY ||--o{ SLA_TARGET : defines
  SLA_TARGET ||--o{ SLA_TIMER : measures
  SLA_TIMER ||--o{ ESCALATION_RULE : triggers

  KNOWLEDGE_ARTICLE ||--o{ ARTICLE_VERSION : versioned
  KNOWLEDGE_ARTICLE ||--o{ ARTICLE_TAG : tagged

  WORKFLOW ||--o{ WORKFLOW_STEP : contains
  WORKFLOW ||--o{ WORKFLOW_INSTANCE : executes
  WORKFLOW_INSTANCE ||--o{ WORKFLOW_TRANSITION : records

  AUDIT_LOG {
    uuid id
    uuid user_id
    string action
    string entity_type
    uuid entity_id
    string hash
    string prev_hash
    datetime created_at
  }
```

## Notes
- Use UUIDs for all primary keys.
- Immutability: `AUDIT_LOG` stores hash chains (prev_hash, hash).
- Multi-tenancy: all domain entities carry `organization_id`.
