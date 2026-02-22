# ITIL v4 Operational Gap Checklist

Date: 2026-02-14
Scope: ITIL v4 service management practices relevant to operational delivery in this codebase.
Rating: Implemented = evidence in UI/API; Partial = present but missing controls/coverage; Gap = not evident.

## Checklist

| Practice | Status | Evidence | Gaps / Actions |
| --- | --- | --- | --- |
| Incident Management | Implemented | UI detail workflow and major incident handling in [fe/src/pages/Incidents.jsx](fe/src/pages/Incidents.jsx); backend validation for major incident manager and PIR | Verify lifecycle UI actions and confirm PIR completion workflow is enforced end-to-end. |
| Major Incident Management | Implemented | Major incident fields and communications cadence in [fe/src/pages/Incidents.jsx](fe/src/pages/Incidents.jsx); backend enforcement | Add role-based guardrails and formal major incident review checklist if required by policy. |
| Service Request Management | Implemented | Approval and fulfillment actions in [fe/src/pages/ServiceRequests.jsx](fe/src/pages/ServiceRequests.jsx) | Confirm approvals routing rules and fulfillment SLAs in backend are fully covered by tests. |
| Change Enablement | Partial | Change detail UI in [fe/src/pages/Changes.jsx](fe/src/pages/Changes.jsx); backend status transitions | Add UI actions for submit/approve/implement/complete with status-based gating. |
| Problem Management | Partial | Problem list UI in [fe/src/pages/Problems.jsx](fe/src/pages/Problems.jsx); backend validation for RCA before resolve | Add problem detail UI for RCA capture, known error, workaround, and resolution workflow. |
| Service Configuration Management | Implemented | CMDB validation and impact analysis in backend | Add UI prompts for relationship requirements and impact analysis completion in CMDB view. |
| Knowledge Management | Implemented | Lifecycle and publish gating in knowledge UI; backend RBAC and checklist | Ensure review notes, publish checklist, and archival reporting are visible in audit logs. |
| Service Level Management | Partial | SLA/OLA/UC targets displayed in incident and service request UI | Add SLA policy administration, breach notifications, and reporting dashboards. |
| Monitoring and Event Management | Gap | Not evident in current UI/API | Implement event ingestion, correlation, and alert-to-incident automation. |
| Service Desk | Partial | Ticket creation and detail views in UI | Add omnichannel intake (email/chat/portal), contact tracking, and shift handover. |
| Release Management | Gap | Not evident in current UI/API | Implement release records, deployment calendar, and release approval gates. |
| Deployment Management | Gap | Not evident in current UI/API | Add deployment records and integration with change records. |
| IT Asset Management | Partial | CMDB exists; asset lifecycle not fully evident | Add hardware/software asset lifecycle, financials, and ownership history. |
| Information Security Management | Gap | Not evident in current UI/API | Define controls, risk treatment records, and security incident integration. |
| Availability Management | Gap | Not evident in current UI/API | Add availability targets, tracking, and reporting. |
| Capacity and Performance Management | Gap | Not evident in current UI/API | Add capacity plans, monitoring integrations, and trend analysis. |
| Service Continuity Management | Gap | Not evident in current UI/API | Add continuity plans, testing schedules, and recovery objectives. |
| Supplier Management | Gap | Not evident in current UI/API | Add supplier records, contracts, and performance reviews. |
| Continual Improvement | Partial | Roadmaps and planning docs exist; no workflow | Add improvement register, backlog, and benefit tracking workflow. |
| Service Catalog Management | Partial | Service request categories exist | Add catalog items, pricing, approvals, and lifecycle management. |

## Notes
- This checklist is based on visible application code and does not replace a formal audit.
- Status entries should be revalidated after UI alignment and any new backend enforcement is merged.

## Recommended Next Steps
1. Add UI actions for change and problem workflows to match backend state rules.
2. Build SLA and reporting dashboards for service level management.
3. Define monitoring/event ingestion to reduce manual incident creation.
