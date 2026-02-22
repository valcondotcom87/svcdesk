import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import ModuleCategoryPanel from '../components/ModuleCategoryPanel.jsx'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'asset', label: 'Asset' },
  { key: 'category', label: 'Category' },
  { key: 'lifecycle', label: 'Lifecycle' },
  { key: 'owner', label: 'Owner' },
  { key: 'warranty', label: 'Warranty' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['active', 'in_use', 'in use'].includes(value)) return 'green'
  if (['planned', 'pending'].includes(value)) return 'blue'
  if (['retired', 'disposed'].includes(value)) return 'red'
  return 'amber'
}

export default function Assets({ onCreateTicket }) {
  const navigate = useNavigate()
  const [categoryFilter, setCategoryFilter] = useState('')
  const { data: categoryData } = useApi('/assets/asset-categories/?ordering=name&page_size=200')
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const categoryQuery = categoryFilter ? `&category=${encodeURIComponent(categoryFilter)}` : ''
  const { data, isLoading, reload } = useApi(`/assets/assets/?ordering=name&page_size=10${categoryQuery}`)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const hasFilter = Boolean(categoryFilter)
  const rows = list.map((item) => ({
    id: item.id,
    asset: item.asset_tag || item.name,
    category: item.category_name || 'Asset',
    lifecycle: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status_display || item.status)}
      />
    ),
    owner: item.owner_name || item.current_owner || 'Unassigned',
    warranty: item.warranty_expires || item.purchase_date || 'N/A',
  }))

  useEffect(() => {
    const handler = (event) => {
      if (event?.detail?.type === 'asset') {
        reload()
      }
    }
    window.addEventListener('itsm:ticket-created', handler)
    return () => window.removeEventListener('itsm:ticket-created', handler)
  }, [reload])

  return (
    <div className="fade-in">
      <PageHeader
        title="Asset Management"
        subtitle="Inventory, lifecycle, and ownership tracking"
        actions={(
          <button type="button" onClick={() => onCreateTicket?.('asset')}>
            Register Asset
          </button>
        )}
      />
      <div className="banner" style={{ marginBottom: '1rem' }}>
        <strong>Asset reporting and dashboards</strong>
        <div className="muted" style={{ marginTop: '0.35rem' }}>
          Keep track of all assets with real-time dashboards for total assets, workstations,
          software, purchase orders, contracts, and more out of the box.
        </div>
        <div className="muted" style={{ marginTop: '0.35rem' }}>
          Create standard, custom, and audit reports to support compliance and planning.
        </div>
        <div style={{ marginTop: '0.5rem' }}>
          <button type="button" onClick={() => navigate('/assets-dashboard')}>
            Open Asset Dashboard
          </button>
        </div>
      </div>
      <div className="form-grid" style={{ marginBottom: '1rem' }}>
        <div className="form-field">
          <label>Category</label>
          <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}>
            <option value="">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>{category.name}</option>
            ))}
          </select>
        </div>
      </div>
      {!isLoading && rows.length === 0 ? (
        <div className="banner" style={{ marginBottom: '1rem' }}>
          <strong>{hasFilter ? 'No assets match this category' : 'No assets registered'}</strong>
          <div className="muted">
            {hasFilter
              ? 'Clear the filter or pick another category to see assets.'
              : 'Register assets to track ownership, warranty, and lifecycle status.'}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            {hasFilter ? (
              <button type="button" onClick={() => setCategoryFilter('')}>Clear filter</button>
            ) : (
              <button type="button" onClick={() => navigate('/knowledge')}>Search Knowledge</button>
            )}
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('asset')}>
              Register Asset
            </button>
          </div>
        </div>
      ) : null}
      <DataTable columns={columns} rows={rows} isLoading={isLoading} emptyMessage="No assets found." />
      <ModuleCategoryPanel moduleKey="assets" title="Asset Categories" />
    </div>
  )
}
