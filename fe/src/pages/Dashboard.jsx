import { useNavigate } from 'react-router-dom'
import MetricCard from '../components/MetricCard.jsx'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import { useApi } from '../api/hooks.js'

const incidentColumns = [
  { key: 'ticket', label: 'Ticket' },
  { key: 'summary', label: 'Summary' },
  { key: 'priority', label: 'Priority' },
  { key: 'breach', label: 'Breaches' },
  { key: 'owner', label: 'Owner' },
]

const changeColumns = [
  { key: 'change', label: 'Change' },
  { key: 'type', label: 'Type' },
  { key: 'risk', label: 'Risk' },
  { key: 'window', label: 'Window' },
]

const priorityTone = (priority) => {
  const value = String(priority || '').toLowerCase()
  if (value.includes('critical') || value === '1') return 'critical'
  if (value.includes('high') || value === '2') return 'high'
  if (value.includes('medium') || value === '3') return 'medium'
  return 'low'
}

const priorityRank = (priority) => {
  const value = String(priority || '').toLowerCase()
  if (value.includes('critical') || value === '1') return 1
  if (value.includes('high') || value === '2') return 2
  if (value.includes('medium') || value === '3') return 3
  return 4
}

const formatPercent = (value) => (Number.isFinite(value) ? `${value.toFixed(1)}%` : 'N/A')

export default function Dashboard({ showLogin, onLoginClick }) {
  const navigate = useNavigate()
  const { data: incidentData, isLoading: incidentLoading } = useApi('/incidents/incidents/?ordering=-created_at&page_size=5')
  const { data: changeData, isLoading: changeLoading } = useApi('/changes/changes/?ordering=-created_at&page_size=5')
  const { data: slaData } = useApi('/sla/sla-metrics/?ordering=-year,-month&page_size=1')

  const incidentList = Array.isArray(incidentData?.results)
    ? incidentData.results
    : Array.isArray(incidentData)
      ? incidentData
      : []
  const changeList = Array.isArray(changeData?.results)
    ? changeData.results
    : Array.isArray(changeData)
      ? changeData
      : []
  const slaMetrics = Array.isArray(slaData?.results)
    ? slaData.results
    : Array.isArray(slaData)
      ? slaData
      : []
  const latestSla = slaMetrics[0]

  const openIncidents = incidentData?.count ?? incidentList.length
  const completedChanges = changeList.filter((item) => item.status === 'completed').length
  const changeSuccess = changeList.length ? (completedChanges / changeList.length) * 100 : null

  const metrics = [
    { title: 'MTTR (7d)', value: 'N/A', trend: '—', caption: 'Requires SLA metrics' },
    {
      title: 'SLA Compliance',
      value: formatPercent(latestSla?.compliance_percentage),
      trend: latestSla
        ? `${latestSla?.compliance_percentage >= latestSla?.target_compliance ? '+' : '-'}0.0%`
        : '—',
      caption: 'Latest reporting period',
    },
    { title: 'Open Incidents', value: `${openIncidents}`, trend: '—', caption: 'Across all services' },
    { title: 'Change Success', value: formatPercent(changeSuccess), trend: '—', caption: 'Last 5 changes' },
  ]

  const incidentListSorted = [...incidentList].sort((a, b) => {
    const aMajor = a.is_major ? 1 : 0
    const bMajor = b.is_major ? 1 : 0
    if (aMajor !== bMajor) return bMajor - aMajor

    const aBreach = a.sla_breach || a.ola_breach || a.uc_breach ? 1 : 0
    const bBreach = b.sla_breach || b.ola_breach || b.uc_breach ? 1 : 0
    if (aBreach !== bBreach) return bBreach - aBreach

    return priorityRank(a.priority_display || a.priority) - priorityRank(b.priority_display || b.priority)
  })

  const incidentRows = incidentListSorted.map((item) => ({
    id: item.id,
    ticket: (
      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', alignItems: 'center' }}>
        <span>{item.ticket_number}</span>
        {item.is_major && <StatusChip label="Major" tone="critical" />}
      </div>
    ),
    summary: item.title,
    priority: (
      <StatusChip
        label={item.priority_display || item.priority}
        tone={priorityTone(item.priority_display || item.priority)}
      />
    ),
    breach: item.sla_breach || item.ola_breach || item.uc_breach ? (
      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
        {item.sla_breach && <StatusChip label="SLA" tone="breached" />}
        {item.ola_breach && <StatusChip label="OLA" tone="breached" />}
        {item.uc_breach && <StatusChip label="UC" tone="breached" />}
      </div>
    ) : (
      <StatusChip label="On Track" tone="on_track" />
    ),
    owner: item.assigned_to_name || 'Unassigned',
  }))

  const changeRows = changeList.map((item) => ({
    id: item.id,
    change: item.ticket_number,
    type: item.type_display || item.change_type,
    risk: (
      <StatusChip
        label={item.impact_display || item.impact_level}
        tone={priorityTone(item.impact_display || item.impact_level)}
      />
    ),
    window: item.implementation_date ? new Date(item.implementation_date).toLocaleString() : 'TBD',
  }))

  const headerActions = showLogin
    ? <button type="button" onClick={onLoginClick}>Login</button>
    : <button type="button" onClick={() => navigate('/sla-reports')}>Generate Report</button>

  return (
    <div className="fade-in">
      <PageHeader
        title="Executive Dashboard"
        subtitle="Real-time operational posture and SLA health"
        actions={headerActions}
      />

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      <div className="split-grid">
        <div>
          <PageHeader title="Active Incidents" subtitle="Top SLA risk items" />
          <div className="muted" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
            <span>Legend:</span>
            <StatusChip label="SLA" tone="breached" />
            <StatusChip label="OLA" tone="breached" />
            <StatusChip label="UC" tone="breached" />
            <StatusChip label="On Track" tone="on_track" />
            <StatusChip label="Major" tone="critical" />
          </div>
          <DataTable
            columns={incidentColumns}
            rows={incidentRows}
            isLoading={incidentLoading}
            emptyMessage="No incidents found."
          />
        </div>
        <div>
          <PageHeader title="Change Calendar" subtitle="Next 72 hours" />
          <DataTable
            columns={changeColumns}
            rows={changeRows}
            isLoading={changeLoading}
            emptyMessage="No changes scheduled."
          />
        </div>
      </div>
    </div>
  )
}
