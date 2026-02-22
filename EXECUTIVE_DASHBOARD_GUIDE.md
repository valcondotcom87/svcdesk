# Executive Dashboard - Documentation

## Overview
The Executive Dashboard provides strategic oversight and key performance indicators (KPIs) for management and executive teams. It offers a high-level view of IT service management operations with actionable insights and trend analysis.

## Features

### 1. Key Performance Indicators (KPIs)
Four primary KPI cards at the top of the dashboard:

- **SLA Compliance**
  - Current compliance percentage
  - Comparison to target (default: 95%)
  - Trend indicator showing improvement or decline
  - Color-coded status (green: meeting target, orange: below target)

- **Open Incidents**
  - Total number of open incidents
  - Critical incidents count highlighted
  - Color-coded alert (red if critical incidents exist)

- **Change Success Rate**
  - Percentage of successful changes
  - Trend showing recent improvement
  - Based on last 100 changes
  - Color-coded (green: ≥95%, orange: <95%)

- **Average Resolution Time (MTTR)**
  - Mean Time To Resolve across all incidents
  - Displayed in hours
  - Calculated from resolved/closed incidents only

### 2. Service Health Overview
Three summary cards showing operational status:

- **Total Incidents**: Overall incident count with open incidents breakdown
- **Problems**: Total problems with open problems count
- **Service Requests**: Total requests with pending count

### 3. Top Priority Open Incidents
Table showing up to 10 highest-priority open incidents:
- Ticket number
- Summary (truncated to 50 characters)
- Priority (color-coded chip)
- Status
- Age in days

Sorted by priority: Critical → High → Medium → Low

### 4. SLA Compliance Trend
Historical view of last 6 months:
- Period (Year-Month)
- Total incidents
- Breached incidents
- Compliance percentage

### 5. Operational Metrics Detail
Comprehensive breakdown across four categories:

**Incident Management**
- Total incidents count
- Open incidents
- Critical incidents
- Average resolution time

**Change Management**
- Success rate percentage
- Total changes count

**Problem Management**
- Total problems
- Open problems count

**Service Level Agreement**
- Current compliance percentage
- Target compliance percentage

### 6. Strategic Insights & Recommendations
Automatic analysis and recommendations based on current metrics:

- **SLA Below Target Warning**: Alerts when compliance falls below target
- **Critical Incidents Alert**: Highlights when critical incidents require attention
- **Change Management Success**: Positive feedback when success rate exceeds 95%
- **Open Problems Notice**: Recommends resource allocation when >5 problems open

## User Interface

### Time Range Filter
Select reporting period:
- Last 7 Days
- Last 30 Days (default)
- Last 90 Days
- Last 12 Months

### Actions
- **Refresh**: Manual data refresh
- **Export Report**: Export dashboard data to JSON format

### Auto-Refresh
Dashboard automatically refreshes every 5 minutes to ensure data is current. Last update time displayed below header.

## Data Sources

The dashboard aggregates data from multiple API endpoints:

```javascript
/api/v1/incidents/incidents/          // Incidents data
/api/v1/changes/changes/              // Changes data
/api/v1/problems/problems/            // Problems data
/api/v1/sla/sla-metrics/              // SLA metrics
/api/v1/service-requests/service-requests/  // Service requests
```

## Metrics Calculations

### SLA Compliance
```
SLA Compliance % = (Total Incidents - Breached) / Total Incidents × 100
```

### Change Success Rate
```
Change Success Rate % = Successful Changes / Total Changes × 100
```

### Average Resolution Time (MTTR)
```
MTTR = Σ(Resolved Time - Created Time) / Number of Resolved Incidents
```
- Only includes incidents with both created_at and resolved_at timestamps
- Displayed in hours

### Incident Age
```
Age (days) = (Current Date - Created Date) / 86400 seconds
```

## Color Coding

### Status Indicators
- **Green**: Meeting or exceeding targets (success)
- **Orange**: Below target but not critical (warning)
- **Red**: Critical attention required (critical)
- **Blue**: Informational (info)
- **Gray**: Neutral/normal (normal)

### Priority Levels
- **Critical**: Red background
- **High**: Orange background
- **Medium**: Yellow background
- **Low**: Gray background

## Navigation

From the Executive Dashboard, users can drill down to detailed views:

- **View All Incidents** button → Incidents page
- **View Detailed Report** button → SLA Reports page

## Export Functionality

### JSON Export Format
Exported report includes:
```json
{
  "generatedAt": "ISO timestamp",
  "period": "time range selected",
  "kpis": [...],
  "serviceHealth": [...],
  "topIncidents": [...],
  "slaTrend": [...],
  "summary": {
    "totalIncidents": number,
    "openIncidents": number,
    "criticalIncidents": number,
    "slaCompliance": number,
    "changeSuccessRate": number,
    "openProblems": number,
    "avgResolutionTime": number
  }
}
```

File naming convention: `executive-report-YYYY-MM-DD.json`

## Access Control

### Recommended Permissions
- **View Access**: Senior management, IT directors, service owners
- **Full Access**: CIO, IT executives, senior leadership

### Role-Based Considerations
- Executives typically have read-only access
- Data visible is organization-scoped (multi-tenant aware)
- Superusers see all organizations' data

## Best Practices

### For Executives
1. **Daily Review**: Check dashboard at start of business day
2. **Focus on Trends**: Monitor week-over-week/month-over-month changes
3. **Act on Insights**: Address recommendations in Strategic Insights section
4. **Export for Meetings**: Use JSON export for board presentations

### For IT Leaders
1. **Set Realistic Targets**: Ensure SLA targets are achievable
2. **Investigate Anomalies**: Drill down when metrics deviate significantly
3. **Resource Planning**: Use open incidents/problems data for staffing decisions
4. **Continuous Improvement**: Track MTTR trends for process optimization

### For Service Managers
1. **Pre-Meeting Preparation**: Review before executive meetings
2. **Explain Variances**: Prepare context for metrics below target
3. **Highlight Successes**: Use positive insights to demonstrate team value
4. **Action Items**: Convert recommendations to team tasks

## Integration with Other Modules

### Dashboard Relationships
```
Executive Dashboard
├── Standard Dashboard (operational view)
├── Incidents Module (drill-down)
├── Changes Module (success rate detail)
├── Problems Module (problem analysis)
└── SLA Reports (compliance detail)
```

### Data Flow
```
API Endpoints → Executive Dashboard → Aggregation → KPI Cards
                                    → Calculations → Metrics
                                    → Analysis → Insights
```

## Performance Considerations

### Auto-Refresh Impact
- Refresh interval: 5 minutes
- API calls per refresh: 5 concurrent requests
- Total data volume: ~250 records per refresh (default page sizes)

### Optimization Tips
1. Use appropriate page_size parameters (current: 50-100)
2. Implement backend caching for frequently accessed metrics
3. Consider pre-aggregating SLA metrics for better performance
4. Monitor API response times if dashboard loads slowly

### Browser Performance
- Renders up to 10 incidents in table (limited for performance)
- SLA trend limited to 6 months
- Efficient React re-rendering with useMemo hooks

## Troubleshooting

### Dashboard Shows No Data
**Possible causes:**
1. No tickets/changes/problems in system yet
2. API endpoints not accessible
3. Authentication token expired

**Solutions:**
- Check browser console for API errors
- Verify backend services are running
- Click Refresh button to reload data

### SLA Compliance Shows N/A
**Cause:** No SLA metrics data available

**Solution:**
- Generate SLA reports from /sla-reports page first
- Wait for SLA calculation job to complete
- Check SLA configuration in Admin panel

### Incorrect Metrics
**Possible causes:**
1. Data not fully synced
2. Cached data displayed
3. Time zone differences

**Solutions:**
- Click manual Refresh button
- Check "Last updated" timestamp
- Clear browser cache if persistent

### Export Not Working
**Cause:** Browser blocking download or JSON generation error

**Solution:**
- Check browser console for errors
- Ensure pop-ups/downloads are allowed
- Try different browser if issue persists

## Future Enhancements

### Planned Features
1. **Interactive Charts**: Replace tables with visual charts (Chart.js/Recharts)
2. **Customizable KPIs**: Allow executives to choose which metrics to display
3. **Comparison View**: Compare current period vs. previous period
4. **PDF Export**: Generate formatted PDF reports for printing
5. **Email Digests**: Scheduled daily/weekly email reports
6. **Drill-Down**: Click metrics to view detailed breakdowns
7. **Forecast Trends**: Predictive analysis for upcoming periods
8. **Custom Alerts**: Set thresholds for automated notifications

### Technical Improvements
1. **Real-time Updates**: WebSocket integration for live data
2. **Advanced Filtering**: Filter by organization, team, service
3. **Historical Comparison**: Year-over-year, quarter-over-quarter views
4. **Mobile Optimization**: Responsive design for tablets/phones
5. **Dashboard Widgets**: Drag-and-drop customizable layout

## API Endpoints Reference

### Required Endpoints
```
GET /api/v1/incidents/incidents/?page_size=100
GET /api/v1/changes/changes/?page_size=100
GET /api/v1/problems/problems/?page_size=50
GET /api/v1/sla/sla-metrics/?ordering=-year,-month&page_size=6
GET /api/v1/service-requests/service-requests/?page_size=100
```

### Expected Response Format
All endpoints should return:
```json
{
  "count": number,
  "next": string|null,
  "previous": string|null,
  "results": [...]
}
```

## Support and Contact

For technical support or feature requests related to the Executive Dashboard:
1. Review this documentation first
2. Check application logs for errors
3. Contact IT Service Management team
4. Submit feature requests through system feedback

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Module:** Executive Dashboard  
**Access Level:** Executive/Management
