import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import ModuleCategoryPanel from '../components/ModuleCategoryPanel.jsx'
import { apiRequest } from '../api/client.js'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'change', label: 'Change' },
  { key: 'type', label: 'Type' },
  { key: 'risk', label: 'Risk' },
  { key: 'cab', label: 'CAB' },
  { key: 'window', label: 'Window' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['approved', 'completed'].includes(value)) return 'green'
  if (['rejected', 'rolled_back'].includes(value)) return 'red'
  if (['pending_approval', 'submitted', 'in_progress'].includes(value)) return 'amber'
  return 'blue'
}

const impactTone = (impact) => {
  const value = String(impact || '').toLowerCase()
  if (value.includes('critical') || value === '1') return 'critical'
  if (value.includes('high') || value === '2') return 'high'
  if (value.includes('medium') || value === '3') return 'medium'
  return 'low'
}

export default function Changes({ onCreateTicket }) {
  const navigate = useNavigate()
  const [categoryFilter, setCategoryFilter] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailChange, setDetailChange] = useState(null)
  const [selectedChangeId, setSelectedChangeId] = useState(null)
  const [actionComment, setActionComment] = useState('')
  const [actionError, setActionError] = useState('')
  const [actionSubmitting, setActionSubmitting] = useState(false)
  const { data: categoryData } = useApi('/organizations/module-categories/?module=changes&is_active=true&ordering=sort_order&page_size=200')
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const categoryQuery = categoryFilter ? `&category=${encodeURIComponent(categoryFilter)}` : ''
  const { data, isLoading, reload } = useApi(`/changes/changes/?ordering=-created_at&page_size=10${categoryQuery}`)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const hasFilter = Boolean(categoryFilter)
  const rows = list.map((item) => ({
    id: item.id,
    change: item.ticket_number,
    type: item.type_display || item.change_type,
    risk: (
      <StatusChip
        label={item.impact_display || item.impact_level}
        tone={impactTone(item.impact_display || item.impact_level)}
      />
    ),
    cab: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    window: item.implementation_date ? new Date(item.implementation_date).toLocaleString() : 'TBD',
  }))

  const formatDate = (value) => {
    if (!value) return 'Not scheduled'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toLocaleString()
  }

  const openDetail = (changeId) => {
    if (!changeId) return
    setSelectedChangeId(changeId)
    setDetailOpen(true)
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailChange(null)
    setDetailError('')
    setActionComment('')
    setActionError('')
  }

  const loadDetail = (changeId) => {
    if (!changeId) return
    setDetailLoading(true)
    setDetailError('')
    apiRequest(`/changes/changes/${changeId}/`)
      .then((payload) => {
        setDetailChange(payload)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load change details.'
        setDetailError(message)
      })
      .finally(() => {
        setDetailLoading(false)
      })
  }

  const handleAction = async (action) => {
    if (!detailChange?.id || actionSubmitting) return
    if (['approve', 'reject'].includes(action) && !actionComment.trim()) {
      setActionError('Approval notes are required for approve/reject decisions.')
      return
    }
    setActionSubmitting(true)
    setActionError('')
    try {
      const body = ['approve', 'reject'].includes(action)
        ? { comments: actionComment.trim() }
        : undefined

      await apiRequest(`/changes/changes/${detailChange.id}/${action}/`, {
        method: 'POST',
        body,
      })
      setActionComment('')
      reload()
      loadDetail(detailChange.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to perform action.'
      setActionError(message)
    } finally {
      setActionSubmitting(false)
    }
  }

  useEffect(() => {
    if (!detailOpen || !selectedChangeId) return
    loadDetail(selectedChangeId)
  }, [detailOpen, selectedChangeId])

  useEffect(() => {
    const handler = (event) => {
      if (event?.detail?.type === 'change') {
        reload()
      }
    }
    window.addEventListener('itsm:ticket-created', handler)
    return () => window.removeEventListener('itsm:ticket-created', handler)
  }, [reload])

  return (
    <div className="fade-in">
      <PageHeader
        title="Change Enablement"
        subtitle="Risk scoring, CAB approvals, and change calendar"
        actions={(
          <button type="button" onClick={() => onCreateTicket?.('change')}>
            New Change
          </button>
        )}
      />
      <div className="form-grid" style={{ marginBottom: '1rem' }}>
        <div className="form-field">
          <label>Category</label>
          <select value={categoryFilter} onChange={(event) => setCategoryFilter(event.target.value)}>
            <option value="">All categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.name}>{category.name}</option>
            ))}
          </select>
        </div>
      </div>
      {!isLoading && rows.length === 0 ? (
        <div className="banner" style={{ marginBottom: '1rem' }}>
          <strong>{hasFilter ? 'No changes match this category' : 'No changes scheduled'}</strong>
          <div className="muted">
            {hasFilter
              ? 'Clear the filter or pick another category to see changes.'
              : 'Submit a change request to begin risk review and CAB approval.'}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            {hasFilter ? (
              <button type="button" onClick={() => setCategoryFilter('')}>Clear filter</button>
            ) : (
              <button type="button" onClick={() => navigate('/incidents')}>View Incidents</button>
            )}
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('change')}>
              New Change
            </button>
          </div>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No changes found."
        onRowClick={(row) => openDetail(row.id)}
      />
      <ModuleCategoryPanel moduleKey="changes" title="Change Categories" />

      {detailOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Change detail"
            style={{ maxWidth: '760px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Change Detail</h2>
                <p className="muted">CAB approvals, risk, and implementation plan.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading change details...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailChange && (
                <div className="form-grid">
                  <div className="form-field">
                    <label>Ticket</label>
                    <div>{detailChange.ticket_number}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailChange.status_display || detailChange.status}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Title</label>
                    <div>{detailChange.title}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Description</label>
                    <div>{detailChange.description}</div>
                  </div>
                  <div className="form-field">
                    <label>Category</label>
                    <div>{detailChange.category || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Type</label>
                    <div>{detailChange.type_display || detailChange.change_type}</div>
                  </div>
                  <div className="form-field">
                    <label>Impact</label>
                    <div>{detailChange.impact_display || detailChange.impact_level}</div>
                  </div>
                  <div className="form-field">
                    <label>Requester</label>
                    <div>{detailChange.requester_name || 'Unknown'}</div>
                  </div>
                  <div className="form-field">
                    <label>Implementation owner</label>
                    <div>{detailChange.implementation_owner_name || 'Unassigned'}</div>
                  </div>
                  <div className="form-field">
                    <label>Planned start</label>
                    <div>{formatDate(detailChange.implementation_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>Planned end</label>
                    <div>{formatDate(detailChange.backout_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>Estimated duration</label>
                    <div>{detailChange.estimated_duration_minutes ? `${detailChange.estimated_duration_minutes} minutes` : 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Affected CI/service</label>
                    <div>{detailChange.affected_services || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Risk assessment</label>
                    <div>{detailChange.risk_assessment || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Risk mitigation</label>
                    <div>{detailChange.risk_mitigation || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Implementation plan</label>
                    <div>{detailChange.implementation_plan || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Backout plan</label>
                    <div>{detailChange.backout_plan || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Test/validation plan</label>
                    <div>{detailChange.success_criteria || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Test results</label>
                    <div>{detailChange.test_results || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>CAB members</label>
                    {Array.isArray(detailChange.cab_members) && detailChange.cab_members.length > 0 ? (
                      <div className="muted">
                        {detailChange.cab_members.map((member) => (
                          <div key={member.id}>
                            {member.user_name || member.user} - {member.role}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No CAB members assigned.</div>
                    )}
                  </div>
                  <div className="form-field form-field-full">
                    <label>Approvals</label>
                    {Array.isArray(detailChange.approvals) && detailChange.approvals.length > 0 ? (
                      <div className="muted">
                        {detailChange.approvals.map((approval) => (
                          <div key={approval.id}>
                            {approval.cab_member_name || approval.cab_member} - {approval.status_display || approval.status}
                            {approval.decided_at ? ` (${formatDate(approval.decided_at)})` : ''}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No approvals recorded.</div>
                    )}
                  </div>

                  {(detailChange.status === 'draft'
                    || detailChange.status === 'pending_approval'
                    || detailChange.status === 'approved'
                    || detailChange.status === 'in_progress') && (
                    <div className="form-field form-field-full">
                      <label>Actions</label>
                      {actionError && <div className="banner">{actionError}</div>}
                      {detailChange.status === 'draft' && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <button type="button" onClick={() => handleAction('submit')} disabled={actionSubmitting}>
                            {actionSubmitting ? 'Submitting...' : 'Submit for CAB'}
                          </button>
                        </div>
                      )}
                      {detailChange.status === 'pending_approval' && (
                        <>
                          <textarea
                            rows={3}
                            value={actionComment}
                            onChange={(event) => setActionComment(event.target.value)}
                            placeholder="CAB approval notes"
                          />
                          {!actionComment.trim() && (
                            <div className="muted" style={{ marginTop: '0.35rem' }}>
                              Required for approve/reject actions.
                            </div>
                          )}
                          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
                            <button
                              type="button"
                              onClick={() => handleAction('approve')}
                              disabled={actionSubmitting || !actionComment.trim()}
                            >
                              {actionSubmitting ? 'Processing...' : 'Approve'}
                            </button>
                            <button
                              type="button"
                              className="ghost"
                              onClick={() => handleAction('reject')}
                              disabled={actionSubmitting || !actionComment.trim()}
                            >
                              Reject
                            </button>
                          </div>
                        </>
                      )}
                      {detailChange.status === 'approved' && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <button type="button" onClick={() => handleAction('implement')} disabled={actionSubmitting}>
                            {actionSubmitting ? 'Starting...' : 'Start Implementation'}
                          </button>
                        </div>
                      )}
                      {detailChange.status === 'in_progress' && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <button type="button" onClick={() => handleAction('complete')} disabled={actionSubmitting}>
                            {actionSubmitting ? 'Completing...' : 'Mark Completed'}
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
