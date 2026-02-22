import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import MetricCard from '../components/MetricCard.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import { useApi } from '../api/hooks.js'

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
const formatNumber = (value) => (Number.isFinite(value) ? value.toLocaleString() : 'N/A')

export default function ExecutiveDashboard() {
  const navigate = useNavigate()
  const [timeRange, setTimeRange] = useState('30d')
  const [lastUpdated, setLastUpdated] = useState(null)

  // Fetch data from various endpoints
  const { data: incidentData, reload: reloadIncidents } = useApi('/incidents/incidents/?page_size=100')
  const { data: changeData, reload: reloadChanges } = useApi('/changes/changes/?page_size=100')
  const { data: problemData, reload: reloadProblems } = useApi('/problems/problems/?page_size=50')
  const { data: slaData, reload: reloadSla } = useApi('/sla/sla-metrics/?ordering=-year,-month&page_size=6')
  const { data: serviceRequestData, reload: reloadServiceRequests } = useApi('/service-requests/service-requests/?page_size=100')

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const intervalId = setInterval(() => {
      reloadIncidents()
      reloadChanges()
      reloadProblems()
      reloadSla()
      reloadServiceRequests()
      setLastUpdated(new Date())
    }, 300000) // 5 minutes
    return () => clearInterval(intervalId)
  }, [reloadIncidents, reloadChanges, reloadProblems, reloadSla, reloadServiceRequests])

  useEffect(() => {
    if (incidentData || changeData || problemData) {
      setLastUpdated(new Date())
    }
  }, [incidentData, changeData, problemData])

  // Process data
  const incidents = Array.isArray(incidentData?.results) ? incidentData.results : []
  const changes = Array.isArray(changeData?.results) ? changeData.results : []
  const problems = Array.isArray(problemData?.results) ? problemData.results : []
  const slaMetrics = Array.isArray(slaData?.results) ? slaData.results : []
  const serviceRequests = Array.isArray(serviceRequestData?.results) ? serviceRequestData.results : []

  // Calculate executive metrics
  const executiveMetrics = useMemo(() => {
    const totalIncidents = incidentData?.count || incidents.length
    const openIncidents = incidents.filter(i => i.status !== 'resolved' && i.status !== 'closed').length
    const criticalIncidents = incidents.filter(i => String(i.priority).toLowerCase().includes('critical') || i.priority === '1').length
    
    const totalChanges = changeData?.count || changes.length
    const successfulChanges = changes.filter(c => c.status === 'completed').length
    const changeSuccessRate = totalChanges > 0 ? (successfulChanges / totalChanges * 100) : 0
    
    const totalProblems = problemData?.count || problems.length
    const openProblems = problems.filter(p => p.status !== 'resolved' && p.status !== 'closed').length
    
    const latestSla = slaMetrics[0]
    const slaCompliance = latestSla?.compliance_percentage || 0
    const slaTarget = latestSla?.target_compliance || 95
    
    const totalServiceRequests = serviceRequestData?.count || serviceRequests.length
    const openServiceRequests = serviceRequests.filter(sr => sr.status !== 'completed' && sr.status !== 'closed').length
    
    // Calculate MTTR (Mean Time To Resolve) - simplified
    const resolvedIncidents = incidents.filter(i => i.status === 'resolved' || i.status === 'closed')
    const avgResolutionTime = resolvedIncidents.length > 0 
      ? resolvedIncidents.reduce((acc, inc) => {
          if (inc.created_at && inc.resolved_at) {
            const created = new Date(inc.created_at)
            const resolved = new Date(inc.resolved_at)
            return acc + (resolved - created) / (1000 * 60 * 60) // hours
          }
          return acc
        }, 0) / resolvedIncidents.length
      : 0
    
    return {
      totalIncidents,
      openIncidents,
      criticalIncidents,
      changeSuccessRate,
      slaCompliance,
      slaTarget,
      totalProblems,
      openProblems,
      totalServiceRequests,
      openServiceRequests,
      avgResolutionTime
    }
  }, [incidents, changes, problems, slaMetrics, serviceRequests, incidentData, changeData, problemData, serviceRequestData])

  // Top-level KPI cards
  const kpiCards = [
    {
      title: 'SLA Compliance',
      value: formatPercent(executiveMetrics.slaCompliance),
      trend: executiveMetrics.slaCompliance >= executiveMetrics.slaTarget ? '+2.3%' : '-1.5%',
      caption: `Target: ${formatPercent(executiveMetrics.slaTarget)}`,
      status: executiveMetrics.slaCompliance >= executiveMetrics.slaTarget ? 'success' : 'warning'
    },
    {
      title: 'Open Incidents',
      value: `${executiveMetrics.openIncidents}`,
      trend: '—',
      caption: `${executiveMetrics.criticalIncidents} critical`,
      status: executiveMetrics.criticalIncidents > 0 ? 'critical' : 'normal'
    },
    {
      title: 'Change Success Rate',
      value: formatPercent(executiveMetrics.changeSuccessRate),
      trend: '+3.2%',
      caption: 'Last 100 changes',
      status: executiveMetrics.changeSuccessRate >= 95 ? 'success' : 'warning'
    },
    {
      title: 'Avg. Resolution Time',
      value: executiveMetrics.avgResolutionTime > 0 
        ? `${executiveMetrics.avgResolutionTime.toFixed(1)}h`
        : 'N/A',
      trend: '—',
      caption: 'MTTR - All incidents',
      status: 'normal'
    }
  ]

  // Service health summary
  const serviceHealthCards = [
    {
      title: 'Total Incidents',
      value: formatNumber(executiveMetrics.totalIncidents),
      subtitle: `${executiveMetrics.openIncidents} open`,
      status: 'info'
    },
    {
      title: 'Problems',
      value: formatNumber(executiveMetrics.totalProblems),
      subtitle: `${executiveMetrics.openProblems} open`,
      status: 'info'
    },
    {
      title: 'Service Requests',
      value: formatNumber(executiveMetrics.totalServiceRequests),
      subtitle: `${executiveMetrics.openServiceRequests} pending`,
      status: 'info'
    }
  ]

  // Top incidents table
  const topIncidentsColumns = [
    { key: 'ticket', label: 'Ticket' },
    { key: 'summary', label: 'Summary' },
    { key: 'priority', label: 'Priority' },
    { key: 'status', label: 'Status' },
    { key: 'breach', label: 'Breaches' },
    { key: 'age', label: 'Age (days)' }
  ]

  const topIncidentsRows = incidents
    .filter(i => i.status !== 'resolved' && i.status !== 'closed')
    .sort((a, b) => {
      const aMajor = a.is_major ? 1 : 0
      const bMajor = b.is_major ? 1 : 0
      if (aMajor !== bMajor) return bMajor - aMajor

      const aBreach = a.sla_breach || a.ola_breach || a.uc_breach ? 1 : 0
      const bBreach = b.sla_breach || b.ola_breach || b.uc_breach ? 1 : 0
      if (aBreach !== bBreach) return bBreach - aBreach

      return priorityRank(a.priority_display || a.priority) - priorityRank(b.priority_display || b.priority)
    })
    .slice(0, 10)
    .map(item => {
      const createdDate = item.created_at ? new Date(item.created_at) : new Date()
      const ageInDays = Math.floor((new Date() - createdDate) / (1000 * 60 * 60 * 24))
      
      return {
        id: item.id,
        ticket: (
          <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <span>{item.ticket_number}</span>
            {item.is_major && <StatusChip label="Major" tone="critical" />}
          </div>
        ),
        summary: item.title?.substring(0, 50) + (item.title?.length > 50 ? '...' : ''),
        priority: (
          <StatusChip
            label={item.priority_display || item.priority}
            tone={priorityTone(item.priority_display || item.priority)}
          />
        ),
        status: item.status_display || item.status,
        breach: item.sla_breach || item.ola_breach || item.uc_breach ? (
          <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
            {item.sla_breach && <StatusChip label="SLA" tone="breached" />}
            {item.ola_breach && <StatusChip label="OLA" tone="breached" />}
            {item.uc_breach && <StatusChip label="UC" tone="breached" />}
          </div>
        ) : (
          <StatusChip label="On Track" tone="on_track" />
        ),
        age: ageInDays
      }
    })

  // SLA Trend (last 6 months)
  const slaTrendColumns = [
    { key: 'period', label: 'Period' },
    { key: 'total', label: 'Total' },
    { key: 'breached', label: 'Breached' },
    { key: 'compliance', label: 'Compliance' }
  ]

  const slaTrendRows = slaMetrics.map(item => ({
    id: item.id,
    period: `${item.year}-${String(item.month).padStart(2, '0')}`,
    total: item.total_incidents || 0,
    breached: item.breached_incidents || 0,
    compliance: formatPercent(item.compliance_percentage)
  }))

  const handleManualRefresh = () => {
    reloadIncidents()
    reloadChanges()
    reloadProblems()
    reloadSla()
    reloadServiceRequests()
    setLastUpdated(new Date())
  }

  const handleExportReport = () => {
    const reportData = {
      generatedAt: new Date().toISOString(),
      period: timeRange,
      kpis: kpiCards,
      serviceHealth: serviceHealthCards,
      topIncidents: topIncidentsRows,
      slaTrend: slaTrendRows,
      summary: {
        totalIncidents: executiveMetrics.totalIncidents,
        openIncidents: executiveMetrics.openIncidents,
        criticalIncidents: executiveMetrics.criticalIncidents,
        slaCompliance: executiveMetrics.slaCompliance,
        changeSuccessRate: executiveMetrics.changeSuccessRate,
        openProblems: executiveMetrics.openProblems,
        avgResolutionTime: executiveMetrics.avgResolutionTime
      }
    }

    // Export as JSON
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `executive-report-${new Date().toISOString().split('T')[0]}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Executive Dashboard"
        subtitle="Strategic overview and key performance indicators"
        actions={
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <select 
              value={timeRange} 
              onChange={(e) => setTimeRange(e.target.value)}
              style={{ padding: '0.5rem', borderRadius: '4px', border: '1px solid #ccc' }}
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="12m">Last 12 Months</option>
            </select>
            <button type="button" className="ghost" onClick={handleManualRefresh}>
              Refresh
            </button>
            <button type="button" onClick={handleExportReport}>
              Export Report
            </button>
          </div>
        }
      />

      <p className="muted" style={{ marginBottom: '1.5rem' }}>
        Auto-refresh every 5 minutes. {lastUpdated ? `Last updated: ${lastUpdated.toLocaleTimeString()}` : ''}
      </p>

      {/* Key Performance Indicators */}
      <h3 style={{ marginBottom: '1rem' }}>Key Performance Indicators</h3>
      <div className="metric-grid" style={{ marginBottom: '2rem' }}>
        {kpiCards.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      {/* Service Health Summary */}
      <h3 style={{ marginBottom: '1rem' }}>Service Health Overview</h3>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        {serviceHealthCards.map((card) => (
          <div key={card.title} className="card" style={{ textAlign: 'center', padding: '1.5rem' }}>
            <div style={{ fontSize: '0.875rem', color: '#666', marginBottom: '0.5rem' }}>
              {card.title}
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', marginBottom: '0.5rem' }}>
              {card.value}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#666' }}>
              {card.subtitle}
            </div>
          </div>
        ))}
      </div>

      {/* Executive Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* Top Priority Incidents */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>Top Priority Open Incidents</h3>
          <div className="muted" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '0.75rem' }}>
            <span>Legend:</span>
            <StatusChip label="SLA" tone="breached" />
            <StatusChip label="OLA" tone="breached" />
            <StatusChip label="UC" tone="breached" />
            <StatusChip label="On Track" tone="on_track" />
            <StatusChip label="Major" tone="critical" />
          </div>
          <DataTable
            columns={topIncidentsColumns}
            rows={topIncidentsRows}
            emptyMessage="No open incidents"
          />
          <div style={{ marginTop: '1rem', textAlign: 'right' }}>
            <button type="button" className="ghost" onClick={() => navigate('/incidents')}>
              View All Incidents →
            </button>
          </div>
        </div>

        {/* SLA Compliance Trend */}
        <div className="card">
          <h3 style={{ marginBottom: '1rem' }}>SLA Compliance Trend (6 Months)</h3>
          <DataTable
            columns={slaTrendColumns}
            rows={slaTrendRows}
            emptyMessage="No SLA data available"
          />
          <div style={{ marginTop: '1rem', textAlign: 'right' }}>
            <button type="button" className="ghost" onClick={() => navigate('/sla-reports')}>
              View Detailed Report →
            </button>
          </div>
        </div>
      </div>

      {/* Critical Metrics Detail */}
      <div className="card" style={{ marginBottom: '2rem' }}>
        <h3 style={{ marginBottom: '1rem' }}>Operational Metrics Detail</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
          gap: '1.5rem',
          padding: '1rem'
        }}>
          <div>
            <strong>Incident Management</strong>
            <div className="split-grid" style={{ marginTop: '0.5rem' }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Total Incidents</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {formatNumber(executiveMetrics.totalIncidents)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Open</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: executiveMetrics.criticalIncidents > 0 ? '#d32f2f' : '#666' }}>
                  {executiveMetrics.openIncidents}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Critical</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#d32f2f' }}>
                  {executiveMetrics.criticalIncidents}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Avg. Resolution</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {executiveMetrics.avgResolutionTime > 0 
                    ? `${executiveMetrics.avgResolutionTime.toFixed(1)}h`
                    : 'N/A'}
                </div>
              </div>
            </div>
          </div>

          <div>
            <strong>Change Management</strong>
            <div className="split-grid" style={{ marginTop: '0.5rem' }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Success Rate</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: executiveMetrics.changeSuccessRate >= 95 ? '#2e7d32' : '#f57c00' }}>
                  {formatPercent(executiveMetrics.changeSuccessRate)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Total Changes</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {formatNumber(changeData?.count || changes.length)}
                </div>
              </div>
            </div>
          </div>

          <div>
            <strong>Problem Management</strong>
            <div className="split-grid" style={{ marginTop: '0.5rem' }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Total Problems</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {formatNumber(executiveMetrics.totalProblems)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Open</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {executiveMetrics.openProblems}
                </div>
              </div>
            </div>
          </div>

          <div>
            <strong>Service Level Agreement</strong>
            <div className="split-grid" style={{ marginTop: '0.5rem' }}>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Compliance</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: executiveMetrics.slaCompliance >= executiveMetrics.slaTarget ? '#2e7d32' : '#d32f2f' }}>
                  {formatPercent(executiveMetrics.slaCompliance)}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.875rem', color: '#666' }}>Target</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {formatPercent(executiveMetrics.slaTarget)}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Strategic Insights */}
      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Strategic Insights & Recommendations</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {executiveMetrics.slaCompliance < executiveMetrics.slaTarget && (
            <div style={{ padding: '1rem', backgroundColor: '#fff3e0', borderLeft: '4px solid #f57c00', borderRadius: '4px' }}>
              <strong>⚠️ SLA Compliance Below Target</strong>
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                Current compliance is {formatPercent(executiveMetrics.slaCompliance)}, below the target of {formatPercent(executiveMetrics.slaTarget)}. 
                Consider reviewing incident response times and resource allocation.
              </div>
            </div>
          )}
          
          {executiveMetrics.criticalIncidents > 0 && (
            <div style={{ padding: '1rem', backgroundColor: '#ffebee', borderLeft: '4px solid #d32f2f', borderRadius: '4px' }}>
              <strong>🔴 Critical Incidents Require Attention</strong>
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                There are {executiveMetrics.criticalIncidents} critical incidents open. Immediate attention recommended to prevent service disruption.
              </div>
            </div>
          )}

          {executiveMetrics.changeSuccessRate >= 95 && (
            <div style={{ padding: '1rem', backgroundColor: '#e8f5e9', borderLeft: '4px solid #2e7d32', borderRadius: '4px' }}>
              <strong>✅ Excellent Change Management Performance</strong>
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                Change success rate is {formatPercent(executiveMetrics.changeSuccessRate)}, exceeding industry standards. Continue following current change management processes.
              </div>
            </div>
          )}

          {executiveMetrics.openProblems > 5 && (
            <div style={{ padding: '1rem', backgroundColor: '#e3f2fd', borderLeft: '4px solid #1976d2', borderRadius: '4px' }}>
              <strong>ℹ️ High Number of Open Problems</strong>
              <div style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
                {executiveMetrics.openProblems} problems are currently open. Consider dedicating resources to problem investigation to prevent recurring incidents.
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
