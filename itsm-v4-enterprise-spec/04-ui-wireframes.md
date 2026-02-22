# 04. UI Wireframes (React)

## Design Direction (Enterprise-Grade)
- Typography: "Space Grotesk" (headings), "Source Sans 3" (body)
- Visual language: calm industrial neutrals + high-contrast status chips
- Motion: page-load fade + staggered table rows, no excessive micro-animations
- Background: subtle radial gradient + grid texture

### Color Tokens
- `--ink-900`: #0F172A
- `--ink-700`: #334155
- `--steel-500`: #64748B
- `--sand-100`: #F6F3EE
- `--signal-amber`: #F59E0B
- `--signal-red`: #DC2626
- `--signal-green`: #16A34A
- `--accent-cyan`: #0EA5E9

## Global Layout
```
+----------------------------------------------------------------------------------+
| Top Bar: Logo | Global Search | Create Ticket | Notifications | User Menu       |
+----------------------------------------------------------------------------------+
| Sidebar: Dashboard, Incidents, Requests, Problems, Changes, CMDB, Assets, SLA   |
|          Knowledge, Reports, Admin                                              |
+---------------------------+------------------------------------------------------+
| Context Panel             | Main Work Area                                       |
| (Filters / SLA / Status)  | (Tables, forms, details, timeline, graphs)          |
+---------------------------+------------------------------------------------------+
```

## Dashboard
```
+----------------------+----------------------+----------------------+
| MTTR (7d)            | SLA Compliance %     | Open Incidents        |
+----------------------+----------------------+----------------------+
| Major Incidents      | Change Success Rate  | Problem Backlog       |
+----------------------+----------------------+----------------------+
| Trend Graph (Incidents/Week) + Heatmap (Site/Dept)                |
+-------------------------------------------------------------------+
```

## Incident Detail
```
+---------------------------------------------------------------+
| Ticket Header: INC-00123 | Priority | Status | SLA Timer       |
+---------------------------------------------------------------+
| Tabs: Overview | Timeline | Linked CIs | Related | Post Review  |
+---------------------------+-----------------------------------+
| Left Column               | Right Column                      |
| - Summary                 | - Assignee                        |
| - Impact/Urgency Matrix   | - SLA Targets                     |
| - Category                | - Linked Changes/Problems          |
+---------------------------+-----------------------------------+
```

## Service Request Detail
```
+---------------------------------------------------------------+
| SR-00456 | Approval Status | Fulfillment Stage                |
+---------------------------------------------------------------+
| Catalog Item | User Inputs | Approval Matrix | Fulfillment    |
```

## Change Calendar
```
+-----------------------------------------------------------------+
| Month/Week Toggle | Filters (Risk, Type, Service) | Export       |
+-----------------------------------------------------------------+
| Calendar Grid with Change Cards (color by risk)                  |
+-----------------------------------------------------------------+
```

## CMDB Graph View
```
+-----------------------------------------------------------------+
| CI Search | Relationship Depth | Impact Simulation              |
+-----------------------------------------------------------------+
| Graph Canvas (nodes + edges), right panel for CI details         |
+-----------------------------------------------------------------+
```

## Accessibility
- WCAG AA contrast
- Keyboard-first navigation
- ARIA labels for all form fields and modal dialogs
