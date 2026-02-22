import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import ModuleCategoryPanel from '../components/ModuleCategoryPanel.jsx'
import { apiRequest } from '../api/client.js'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'ticket', label: 'Request' },
  { key: 'service', label: 'Service' },
  { key: 'status', label: 'Status' },
  { key: 'approval', label: 'Approval' },
  { key: 'sla', label: 'SLA' },
  { key: 'due', label: 'Due' },
  { key: 'requester', label: 'Requester' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['approved', 'fulfilled', 'closed'].includes(value)) return 'green'
  if (['rejected'].includes(value)) return 'red'
  if (['pending_approval', 'pending', 'in_progress', 'submitted'].includes(value)) return 'amber'
  return 'blue'
}

const approvalLabel = (status) => {
  const value = String(status || '').toLowerCase()
  if (value === 'pending_approval') return 'Pending'
  if (value === 'approved') return 'Approved'
  if (value === 'rejected') return 'Rejected'
  return 'Not Required'
}

export default function ServiceRequests({ onCreateTicket, currentUser }) {
  const navigate = useNavigate()
  const [categoryFilter, setCategoryFilter] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailRequest, setDetailRequest] = useState(null)
  const [selectedRequestId, setSelectedRequestId] = useState(null)
  const [actionComment, setActionComment] = useState('')
  const [actionError, setActionError] = useState('')
  const [actionSubmitting, setActionSubmitting] = useState(false)
  const { data: categoryData } = useApi('/service-requests/service-categories/?ordering=name&page_size=200')
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const categoryQuery = categoryFilter ? `&service__category=${encodeURIComponent(categoryFilter)}` : ''
  const { data, isLoading, reload } = useApi(`/service-requests/service-requests/?ordering=-created_at&page_size=10${categoryQuery}`)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const hasFilter = Boolean(categoryFilter)
  const rows = list.map((item) => ({
    id: item.id,
    ticket: item.ticket_number,
    service: item.service_name || item.title || 'Service Request',
    status: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    approval: (
      <StatusChip
        label={approvalLabel(item.status)}
        tone={statusTone(item.status)}
      />
    ),
    sla: (
      <StatusChip
        label={item.sla_breach ? 'Breached' : 'On Track'}
        tone={item.sla_breach ? 'breached' : 'on_track'}
      />
    ),
    due: item.due_date ? new Date(item.due_date).toLocaleString() : 'N/A',
    requester: item.requester_name || 'Unknown',
  }))

  const isEndUser = currentUser?.role === 'end_user'

  const canApprove = useMemo(() => {
    if (!currentUser) return false
    if (currentUser.is_superuser) return true
    return ['manager', 'asset_manager', 'admin'].includes(currentUser.role)
  }, [currentUser])

  const canFulfill = useMemo(() => {
    if (!currentUser) return false
    if (currentUser.is_superuser) return true
    return !['end_user'].includes(currentUser.role)
  }, [currentUser])

  const formatDate = (value) => {
    if (!value) return 'Not scheduled'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toLocaleString()
  }

  const openDetail = (requestId) => {
    if (!requestId) return
    setSelectedRequestId(requestId)
    setDetailOpen(true)
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailRequest(null)
    setDetailError('')
    setActionComment('')
    setActionError('')
  }

  const loadDetail = (requestId) => {
    if (!requestId) return
    setDetailLoading(true)
    setDetailError('')
    apiRequest(`/service-requests/service-requests/${requestId}/`)
      .then((payload) => {
        setDetailRequest(payload)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load request details.'
        setDetailError(message)
      })
      .finally(() => {
        setDetailLoading(false)
      })
  }

  useEffect(() => {
    if (!detailOpen || !selectedRequestId) return
    loadDetail(selectedRequestId)
  }, [detailOpen, selectedRequestId])

  useEffect(() => {
    const handler = (event) => {
      if (event?.detail?.type === 'service_request') {
        reload()
        if (event?.detail?.id) {
          openDetail(event.detail.id)
        }
      }
    }
    window.addEventListener('itsm:ticket-created', handler)
    return () => window.removeEventListener('itsm:ticket-created', handler)
  }, [reload])

  const handleAction = async (action) => {
    if (!detailRequest?.id || actionSubmitting) return
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

      await apiRequest(`/service-requests/service-requests/${detailRequest.id}/${action}/`, {
        method: 'POST',
        body,
      })
      setActionComment('')
      reload()
      loadDetail(detailRequest.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to perform action.'
      setActionError(message)
    } finally {
      setActionSubmitting(false)
    }
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Service Requests"
        subtitle="Catalog-driven requests with approvals and fulfillment workflows"
        actions={(
          <button type="button" onClick={() => onCreateTicket?.('service_request')}>
            New Request
          </button>
        )}
      />
      {isEndUser ? (
        <div className="banner" style={{ marginBottom: '1rem' }}>
          <strong>New here? Start with these steps</strong>
          <div className="muted">1) Search Knowledge. 2) Submit a request. 3) Track status here.</div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            <button type="button" onClick={() => navigate('/knowledge')}>Open Knowledge</button>
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('service_request')}>
              New Request
            </button>
          </div>
        </div>
      ) : null}
      <div className="form-grid" style={{ marginBottom: '1rem' }}>
        <div className="form-field">
          <label>Service category</label>
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
          <strong>{hasFilter ? 'No requests match this category' : 'No requests yet'}</strong>
          <div className="muted">
            {hasFilter
              ? 'Clear the filter or choose another category to see requests.'
              : 'Submit a request or search Knowledge for self-service answers.'}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            {hasFilter ? (
              <button type="button" onClick={() => setCategoryFilter('')}>Clear filter</button>
            ) : (
              <button type="button" onClick={() => navigate('/knowledge')}>Search Knowledge</button>
            )}
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('service_request')}>
              New Request
            </button>
          </div>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No requests found."
        onRowClick={(row) => openDetail(row.id)}
      />
      <div className="muted" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
        <span>Legend:</span>
        <StatusChip label="Breached" tone="breached" />
        <StatusChip label="On Track" tone="on_track" />
      </div>
      <ModuleCategoryPanel moduleKey="service_requests" title="Service Request Categories" />

      {detailOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Service request detail"
            style={{ maxWidth: '720px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Service Request Detail</h2>
                <p className="muted">Approval, fulfillment, and SLA tracking.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading request details...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailRequest && (
                <div className="form-grid">
                  <div className="form-field">
                    <label>Ticket</label>
                    <div>{detailRequest.ticket_number}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailRequest.status_display || detailRequest.status}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Title</label>
                    <div>{detailRequest.title}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Description</label>
                    <div>{detailRequest.description}</div>
                  </div>
                  <div className="form-field">
                    <label>Service</label>
                    <div>{detailRequest.service_name || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Requester</label>
                    <div>{detailRequest.requester_name || 'Unknown'}</div>
                  </div>
                  <div className="form-field">
                    <label>Assigned to</label>
                    <div>{detailRequest.assigned_to_name || 'Unassigned'}</div>
                  </div>
                  <div className="form-field">
                    <label>Due date</label>
                    <div>{formatDate(detailRequest.due_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>SLA due</label>
                    <div>{formatDate(detailRequest.sla_due_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>SLA breach</label>
                    <StatusChip
                      label={detailRequest.sla_breach ? 'Breached' : 'On Track'}
                      tone={detailRequest.sla_breach ? 'breached' : 'on_track'}
                    />
                  </div>
                  <div className="form-field">
                    <label>Submitted</label>
                    <div>{formatDate(detailRequest.submitted_at)}</div>
                  </div>
                  <div className="form-field">
                    <label>Approved</label>
                    <div>{formatDate(detailRequest.approved_at)}</div>
                  </div>
                  <div className="form-field">
                    <label>Fulfilled</label>
                    <div>{formatDate(detailRequest.fulfilled_at)}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Approvals</label>
                    {Array.isArray(detailRequest.approvals) && detailRequest.approvals.length > 0 ? (
                      <div className="muted">
                        {detailRequest.approvals.map((approval) => (
                          <div key={approval.id}>
                            Level {approval.approval_level} - {approval.status} - {approval.approver_name || 'Unassigned'}
                            {approval.decided_at ? ` (${formatDate(approval.decided_at)})` : ''}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No approvals recorded.</div>
                    )}
                  </div>

                  {(detailRequest.status === 'draft' || detailRequest.status === 'pending_approval' || detailRequest.status === 'approved') && (
                    <div className="form-field form-field-full">
                      <label>Actions</label>
                      {actionError && <div className="banner">{actionError}</div>}
                      {(detailRequest.status === 'pending_approval' && canApprove) && (
                        <>
                          <textarea
                            rows={3}
                            value={actionComment}
                            onChange={(event) => setActionComment(event.target.value)}
                            placeholder="Approval notes"
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
                      {(detailRequest.status === 'draft') && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <button type="button" onClick={() => handleAction('submit')} disabled={actionSubmitting}>
                            {actionSubmitting ? 'Submitting...' : 'Submit Request'}
                          </button>
                        </div>
                      )}
                      {(detailRequest.status === 'approved' || detailRequest.status === 'in_progress' || detailRequest.status === 'pending_fulfillment') && canFulfill && (
                        <div style={{ marginTop: '0.5rem' }}>
                          <button type="button" onClick={() => handleAction('complete')} disabled={actionSubmitting}>
                            {actionSubmitting ? 'Completing...' : 'Mark Fulfilled'}
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
