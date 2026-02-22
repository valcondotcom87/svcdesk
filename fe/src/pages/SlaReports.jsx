import { useEffect, useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import MetricCard from '../components/MetricCard.jsx'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'period', label: 'Period' },
  { key: 'total', label: 'Total Incidents' },
  { key: 'breached', label: 'Breached' },
  { key: 'compliance', label: 'Compliance' },
  { key: 'risk', label: 'Risk' },
]

const riskTone = (value, target) => {
  if (value === null || value === undefined) return 'amber'
  if (value >= target) return 'green'
  if (value >= target - 2) return 'amber'
  return 'red'
}

export default function SlaReports() {
  const { data, isLoading, reload } = useApi('/sla/sla-metrics/?ordering=-year,-month&page_size=10')
  const [lastUpdated, setLastUpdated] = useState(null)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const latest = list[0]
  const previous = list[1]

  useEffect(() => {
    if (data) {
      setLastUpdated(new Date())
    }
  }, [data])

  useEffect(() => {
    const intervalId = setInterval(() => {
      reload()
    }, 60000)
    return () => clearInterval(intervalId)
  }, [reload])

  const summaryCards = useMemo(() => {
    if (!latest) {
      return []
    }
    const compliance = Number(latest.compliance_percentage)
    const target = Number(latest.target_compliance)
    const prevCompliance = previous ? Number(previous.compliance_percentage) : null
    const complianceDelta = Number.isFinite(prevCompliance)
      ? `${(compliance - prevCompliance).toFixed(1)}%`
      : '—'
    return [
      {
        title: 'Reporting Period',
        value: `${latest.year}-${String(latest.month).padStart(2, '0')}`,
        trend: '—',
        caption: 'Latest month',
      },
      {
        title: 'Total Incidents',
        value: `${latest.total_incidents ?? 0}`,
        trend: '—',
        caption: 'All SLA tracked',
      },
      {
        title: 'Breached',
        value: `${latest.breached_incidents ?? 0}`,
        trend: '—',
        caption: 'Response or resolution',
      },
      {
        title: 'Compliance',
        value: Number.isFinite(compliance) ? `${compliance.toFixed(1)}%` : 'N/A',
        trend: complianceDelta,
        caption: Number.isFinite(target) ? `Target ${target.toFixed(1)}%` : 'Target unavailable',
      },
    ]
  }, [latest, previous])
  const rows = list.map((item) => {
    const compliance = Number(item.compliance_percentage)
    const target = Number(item.target_compliance)
    const complianceLabel = Number.isFinite(compliance) ? `${compliance.toFixed(1)}%` : 'N/A'
    return {
      id: item.id,
      period: `${item.year}-${String(item.month).padStart(2, '0')}`,
      total: item.total_incidents,
      breached: item.breached_incidents,
      compliance: complianceLabel,
      risk: (
        <StatusChip
          label={Number.isFinite(compliance) && compliance >= target ? 'On Track' : 'At Risk'}
          tone={riskTone(compliance, target)}
        />
      ),
    }
  })

  const exportCsv = () => {
    if (!list.length) {
      return
    }
    const headers = ['Period', 'Total Incidents', 'Breached', 'Compliance', 'Target Compliance', 'Compliant']
    const rows = list.map((item) => [
      `${item.year}-${String(item.month).padStart(2, '0')}`,
      item.total_incidents ?? 0,
      item.breached_incidents ?? 0,
      Number.isFinite(Number(item.compliance_percentage))
        ? `${Number(item.compliance_percentage).toFixed(1)}%`
        : 'N/A',
      Number.isFinite(Number(item.target_compliance))
        ? `${Number(item.target_compliance).toFixed(1)}%`
        : 'N/A',
      item.is_compliant ? 'Yes' : 'No',
    ])
    const csvBody = [headers, ...rows]
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n')
    const blob = new Blob([csvBody], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = 'sla-report.csv'
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="SLA & Reporting"
        subtitle="SLA policy performance and executive KPIs"
        actions={
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button type="button" className="ghost" onClick={reload}>Refresh</button>
            <button type="button" onClick={exportCsv}>Generate Report</button>
          </div>
        }
      />
      <p className="muted">
        Live refresh every 60 seconds.{lastUpdated ? ` Last updated ${lastUpdated.toLocaleTimeString()}.` : ''}
      </p>

      {summaryCards.length ? (
        <div className="metric-grid">
          {summaryCards.map((metric) => (
            <MetricCard key={metric.title} {...metric} />
          ))}
        </div>
      ) : null}

      {latest ? (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3>Report Detail</h3>
          <div className="split-grid">
            <div>
              <strong>Period</strong>
              <div>{`${latest.year}-${String(latest.month).padStart(2, '0')}`}</div>
            </div>
            <div>
              <strong>Compliance</strong>
              <div>
                {Number.isFinite(Number(latest.compliance_percentage))
                  ? `${Number(latest.compliance_percentage).toFixed(1)}%`
                  : 'N/A'}
              </div>
            </div>
            <div>
              <strong>Target</strong>
              <div>
                {Number.isFinite(Number(latest.target_compliance))
                  ? `${Number(latest.target_compliance).toFixed(1)}%`
                  : 'N/A'}
              </div>
            </div>
            <div>
              <strong>Status</strong>
              <div>{latest.is_compliant ? 'Compliant' : 'At Risk'}</div>
            </div>
            <div>
              <strong>Total Incidents</strong>
              <div>{latest.total_incidents ?? 0}</div>
            </div>
            <div>
              <strong>Breached</strong>
              <div>{latest.breached_incidents ?? 0}</div>
            </div>
          </div>
        </div>
      ) : null}

      <DataTable columns={columns} rows={rows} isLoading={isLoading} emptyMessage="No SLA metrics found." />
    </div>
  )
}
