import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import MetricCard from '../components/MetricCard.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import { useApi } from '../api/hooks.js'

const categoryColumns = [
  { key: 'category', label: 'Category' },
  { key: 'count', label: 'Assets' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['in_use'].includes(value)) return 'green'
  if (['in_stock', 'planned'].includes(value)) return 'blue'
  if (['maintenance'].includes(value)) return 'amber'
  if (['retired', 'disposed'].includes(value)) return 'red'
  return 'blue'
}

export default function AssetDashboard() {
  const navigate = useNavigate()
  const [warrantyWindow, setWarrantyWindow] = useState('90')
  const reportPath = useMemo(() => (
    `/assets/assets/report/?warranty_days=${encodeURIComponent(warrantyWindow)}`
  ), [warrantyWindow])
  const { data, isLoading } = useApi(reportPath)

  const metrics = [
    {
      title: 'Total Assets',
      value: data?.total_assets ?? '0',
      trend: '—',
      caption: 'All tracked assets',
    },
    {
      title: 'Workstations',
      value: data?.workstations ?? '0',
      trend: '—',
      caption: 'Desktops and laptops',
    },
    {
      title: 'Software',
      value: data?.software ?? '0',
      trend: '—',
      caption: 'Licensed and managed',
    },
    {
      title: 'Purchase Orders',
      value: data?.purchase_orders ?? '0',
      trend: '—',
      caption: 'Tagged in categories',
    },
    {
      title: 'Contracts',
      value: data?.contracts ?? '0',
      trend: '—',
      caption: 'Tagged in categories',
    },
    {
      title: 'Hardware',
      value: data?.hardware ?? '0',
      trend: '—',
      caption: 'Asset type hardware',
    },
    {
      title: 'Warranty At Risk',
      value: data?.warranty_expiring?.total ?? '0',
      trend: '—',
      caption: `Up to ${data?.warranty_expiring?.days ?? 90} days`,
    },
    {
      title: 'Warranty Expired',
      value: data?.warranty_expiring?.expired ?? '0',
      trend: '—',
      caption: 'Already expired',
    },
    {
      title: 'Warranty Expiring',
      value: data?.warranty_expiring?.expiring ?? '0',
      trend: '—',
      caption: `Next ${data?.warranty_expiring?.days ?? 90} days`,
    },
  ]

  const categoryRows = Array.isArray(data?.top_categories)
    ? data.top_categories.map((item) => ({
      id: item.category,
      category: item.category,
      count: item.count,
    }))
    : []

  const statusRows = Object.entries(data?.status_breakdown || {}).map(([status, count]) => ({
    id: status,
    status: <StatusChip label={status.replace('_', ' ')} tone={statusTone(status)} />,
    count,
  }))

  return (
    <div className="fade-in">
      <PageHeader
        title="Asset Dashboard"
        subtitle="Real-time visibility across inventory, ownership, and spend"
        actions={(
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button type="button" className="ghost" onClick={() => navigate('/assets')}>
              View Assets
            </button>
            <button type="button" onClick={() => navigate('/sla-reports')}>
              Create Report
            </button>
          </div>
        )}
      />

      <div className="banner" style={{ marginBottom: '1rem' }}>
        <strong>Asset reporting</strong>
        <div className="muted" style={{ marginTop: '0.35rem' }}>
          Track total assets, workstations, software, purchase orders, and contracts in one place.
          Use standard, custom, and audit reports to support compliance and budgeting.
        </div>
        <div className="form-grid" style={{ marginTop: '0.75rem' }}>
          <div className="form-field">
            <label>Warranty window (days)</label>
            <select value={warrantyWindow} onChange={(event) => setWarrantyWindow(event.target.value)}>
              <option value="30">30 days</option>
              <option value="60">60 days</option>
              <option value="90">90 days</option>
              <option value="180">180 days</option>
              <option value="365">365 days</option>
            </select>
          </div>
        </div>
      </div>

      <div className="metric-grid">
        {metrics.map((metric) => (
          <MetricCard key={metric.title} {...metric} />
        ))}
      </div>

      <div className="split-grid" style={{ marginTop: '1.5rem' }}>
        <div>
          <PageHeader title="Top Categories" subtitle="Top 10 by asset count" />
          <DataTable
            columns={categoryColumns}
            rows={categoryRows}
            isLoading={isLoading}
            emptyMessage="No categories available."
          />
        </div>
        <div>
          <PageHeader title="Status Breakdown" subtitle="Current lifecycle distribution" />
          <DataTable
            columns={[
              { key: 'status', label: 'Status' },
              { key: 'count', label: 'Assets' },
            ]}
            rows={statusRows}
            isLoading={isLoading}
            emptyMessage="No status data available."
          />
        </div>
      </div>
    </div>
  )
}
