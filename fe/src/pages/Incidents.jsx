import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import ModuleCategoryPanel from '../components/ModuleCategoryPanel.jsx'
import { apiRequest } from '../api/client.js'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'ticket', label: 'Ticket' },
  { key: 'title', label: 'Title' },
  { key: 'priority', label: 'Priority' },
  { key: 'status', label: 'Status' },
  { key: 'breach', label: 'Breaches' },
  { key: 'assignee', label: 'Assignee' },
  { key: 'site', label: 'Site' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['resolved', 'closed'].includes(value)) return 'green'
  if (['reopened'].includes(value)) return 'red'
  if (['in_progress', 'assigned', 'acknowledged', 'on_hold'].includes(value)) return 'amber'
  return 'blue'
}

const priorityTone = (priority) => {
  const value = String(priority || '').toLowerCase()
  if (value.includes('critical') || value === '1') return 'critical'
  if (value.includes('high') || value === '2') return 'high'
  if (value.includes('medium') || value === '3') return 'medium'
  return 'low'
}

export default function Incidents({ onCreateTicket }) {
  const navigate = useNavigate()
  const [categoryFilter, setCategoryFilter] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailIncident, setDetailIncident] = useState(null)
  const [selectedIncidentId, setSelectedIncidentId] = useState(null)
  const [users, setUsers] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [usersError, setUsersError] = useState('')
  const [majorForm, setMajorForm] = useState({
    isMajor: 'no',
    level: '',
    managerId: '',
    escalationStatus: 'not_escalated',
    cadenceMinutes: '60',
  })
  const [majorSubmitting, setMajorSubmitting] = useState(false)
  const [majorError, setMajorError] = useState('')
  const [commForm, setCommForm] = useState({
    channel: 'email',
    audience: 'internal',
    message: '',
  })
  const [commSubmitting, setCommSubmitting] = useState(false)
  const [commError, setCommError] = useState('')
  const [pirForm, setPirForm] = useState({
    required: 'no',
    status: 'not_required',
    ownerId: '',
    summary: '',
    notes: '',
  })
  const [pirSubmitting, setPirSubmitting] = useState(false)
  const [pirError, setPirError] = useState('')
  const { data: categoryData } = useApi('/organizations/module-categories/?module=incidents&is_active=true&ordering=sort_order&page_size=200')
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const categoryQuery = categoryFilter ? `&category=${encodeURIComponent(categoryFilter)}` : ''
  const { data, isLoading, reload } = useApi(`/incidents/incidents/?ordering=-created_at&page_size=10${categoryQuery}`)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const hasFilter = Boolean(categoryFilter)
  const rows = list.map((item) => ({
    id: item.id,
    ticket: item.ticket_number,
    title: item.title,
    priority: (
      <StatusChip
        label={item.priority_display || item.priority}
        tone={priorityTone(item.priority_display || item.priority)}
      />
    ),
    status: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    breach: item.sla_breach || item.ola_breach || item.uc_breach ? (
      <div style={{ display: 'flex', gap: '0.35rem', flexWrap: 'wrap' }}>
        {item.sla_breach && <StatusChip label="SLA" tone="breached" />}
        {item.ola_breach && <StatusChip label="OLA" tone="breached" />}
        {item.uc_breach && <StatusChip label="UC" tone="breached" />}
      </div>
    ) : (
      <span className="muted">On track</span>
    ),
    assignee: item.assigned_to_name || 'Unassigned',
    site: item.affected_service || 'N/A',
  }))

  const formatDate = (value) => {
    if (!value) return 'Not scheduled'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toLocaleString()
  }

  const openDetail = (incidentId) => {
    if (!incidentId) return
    setSelectedIncidentId(incidentId)
    setDetailOpen(true)
  }

  const majorMissingFields =
    majorForm.isMajor === 'yes'
    && (!majorForm.level || !majorForm.managerId || !majorForm.cadenceMinutes)

  const pirMissingFields =
    pirForm.required === 'yes'
    && (!pirForm.ownerId || !pirForm.summary.trim())

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailIncident(null)
    setDetailError('')
  }

  const loadDetail = (incidentId) => {
    if (!incidentId) return
    setDetailLoading(true)
    setDetailError('')
    apiRequest(`/incidents/incidents/${incidentId}/`)
      .then((payload) => {
        setDetailIncident(payload)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load incident details.'
        setDetailError(message)
      })
      .finally(() => {
        setDetailLoading(false)
      })
  }

  useEffect(() => {
    if (!detailOpen || !selectedIncidentId) return
    loadDetail(selectedIncidentId)
  }, [detailOpen, selectedIncidentId])

  useEffect(() => {
    if (!detailOpen) return
    setUsersLoading(true)
    setUsersError('')
    apiRequest('/users/?is_active=true&page_size=200')
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setUsers(list)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load users.'
        setUsersError(message)
        setUsers([])
      })
      .finally(() => {
        setUsersLoading(false)
      })
  }, [detailOpen])

  useEffect(() => {
    if (!detailIncident) return
    setMajorForm({
      isMajor: detailIncident.is_major ? 'yes' : 'no',
      level: detailIncident.major_incident_level || '',
      managerId: detailIncident.major_incident_manager || '',
      escalationStatus: detailIncident.escalation_status || 'not_escalated',
      cadenceMinutes: String(detailIncident.communication_cadence_minutes || 60),
    })
    setPirForm({
      required: detailIncident.pir_required ? 'yes' : 'no',
      status: detailIncident.pir_status || 'not_required',
      ownerId: detailIncident.pir_owner || '',
      summary: detailIncident.pir_summary || '',
      notes: detailIncident.pir_notes || '',
    })
    setCommForm((prev) => ({ ...prev, message: '' }))
    setMajorError('')
    setCommError('')
    setPirError('')
  }, [detailIncident])

  useEffect(() => {
    const handler = (event) => {
      if (event?.detail?.type === 'incident') {
        reload()
        if (event?.detail?.id) {
          openDetail(event.detail.id)
        }
      }
    }
    window.addEventListener('itsm:ticket-created', handler)
    return () => window.removeEventListener('itsm:ticket-created', handler)
  }, [reload])

  const handleMajorUpdate = async () => {
    if (!detailIncident?.id || majorSubmitting) return
    if (majorMissingFields) {
      setMajorError('Major incidents require a level, manager, and communication cadence.')
      return
    }
    setMajorSubmitting(true)
    setMajorError('')
    try {
      await apiRequest(`/incidents/incidents/${detailIncident.id}/`, {
        method: 'PATCH',
        body: {
          is_major: majorForm.isMajor === 'yes',
          major_incident_level: majorForm.isMajor === 'yes' ? majorForm.level || null : null,
          major_incident_manager: majorForm.managerId || null,
          escalation_status: majorForm.escalationStatus || 'not_escalated',
          communication_cadence_minutes: majorForm.isMajor === 'yes' ? Number(majorForm.cadenceMinutes) : null,
        },
      })
      loadDetail(detailIncident.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to update major incident workflow.'
      setMajorError(message)
    } finally {
      setMajorSubmitting(false)
    }
  }

  const handleCommunicationSubmit = async () => {
    if (!detailIncident?.id || commSubmitting) return
    if (!commForm.message.trim()) {
      setCommError('Message is required for communication updates.')
      return
    }
    setCommSubmitting(true)
    setCommError('')
    try {
      await apiRequest(`/incidents/incidents/${detailIncident.id}/add_communication/`, {
        method: 'POST',
        body: {
          channel: commForm.channel,
          audience: commForm.audience,
          message: commForm.message.trim(),
        },
      })
      setCommForm((prev) => ({ ...prev, message: '' }))
      loadDetail(detailIncident.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to add communication.'
      setCommError(message)
    } finally {
      setCommSubmitting(false)
    }
  }

  const handlePirUpdate = async () => {
    if (!detailIncident?.id || pirSubmitting) return
    if (pirMissingFields) {
      setPirError('PIR requires an owner and summary when marked required.')
      return
    }
    setPirSubmitting(true)
    setPirError('')
    try {
      await apiRequest(`/incidents/incidents/${detailIncident.id}/`, {
        method: 'PATCH',
        body: {
          pir_required: pirForm.required === 'yes',
          pir_status: pirForm.required === 'yes' ? pirForm.status : 'not_required',
          pir_owner: pirForm.ownerId || null,
          pir_summary: pirForm.summary.trim(),
          pir_notes: pirForm.notes.trim(),
        },
      })
      loadDetail(detailIncident.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to update post-incident review.'
      setPirError(message)
    } finally {
      setPirSubmitting(false)
    }
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Incident Management"
        subtitle="Priority matrix, SLA timers, and major incident oversight"
        actions={(
          <button type="button" onClick={() => onCreateTicket?.('incident')}>
            New Incident
          </button>
        )}
      />
      <div className="banner" style={{ marginBottom: '1rem' }}>
        <strong>Incident workflow</strong>
        <div className="muted" style={{ marginTop: '0.35rem' }}>
          Incident management starts with detection and logging, then moves through categorization,
          prioritization, and routing to the right technician. The assigned team investigates,
          implements a fix, and restores normal operations. Once resolved, the incident is documented,
          closed, and reviewed when needed to prevent recurrence.
        </div>
        <div className="muted" style={{ marginTop: '0.35rem' }}>
          Use customizable templates to capture key details for major incidents up front so responses
          are consistent and fast.
        </div>
      </div>
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
          <strong>{hasFilter ? 'No incidents match this category' : 'All clear for now'}</strong>
          <div className="muted">
            {hasFilter
              ? 'Clear the filter or try another category to see incidents.'
              : 'Report a new incident or search Knowledge for quick fixes.'}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            {hasFilter ? (
              <button type="button" onClick={() => setCategoryFilter('')}>Clear filter</button>
            ) : (
              <button type="button" onClick={() => navigate('/knowledge')}>Search Knowledge</button>
            )}
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('incident')}>
              Report Incident
            </button>
          </div>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No incidents found."
        onRowClick={(row) => openDetail(row.id)}
      />
      <div className="muted" style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.75rem' }}>
        <span>Legend:</span>
        <StatusChip label="SLA" tone="breached" />
        <StatusChip label="OLA" tone="breached" />
        <StatusChip label="UC" tone="breached" />
        <StatusChip label="On Track" tone="on_track" />
        <StatusChip label="Major" tone="critical" />
      </div>
      <ModuleCategoryPanel moduleKey="incidents" title="Incident Categories" />

      {detailOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Incident detail"
            style={{ maxWidth: '720px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Incident Detail</h2>
                <p className="muted">Major incident overview and communication cadence.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading incident details...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailIncident && (
                <div className="form-grid">
                  <div className="form-field">
                    <label>Ticket</label>
                    <div>{detailIncident.ticket_number}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailIncident.status_display || detailIncident.status}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Title</label>
                    <div>{detailIncident.title}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Description</label>
                    <div>{detailIncident.description}</div>
                  </div>
                  <div className="form-field">
                    <label>Priority</label>
                    <div>{detailIncident.priority_display || detailIncident.priority}</div>
                  </div>
                  <div className="form-field">
                    <label>Major incident</label>
                    <div>{detailIncident.is_major ? 'Yes' : 'No'}</div>
                  </div>
                  <div className="form-field">
                    <label>Major level</label>
                    <div>{detailIncident.major_incident_level || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Communication cadence</label>
                    <div>{detailIncident.communication_cadence_minutes || 'N/A'} minutes</div>
                  </div>
                  <div className="form-field">
                    <label>Next communication due</label>
                    <div>{formatDate(detailIncident.next_communication_due)}</div>
                  </div>
                  <div className="form-field">
                    <label>SLA due</label>
                    <div>{formatDate(detailIncident.sla_due_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>SLA breach</label>
                    <StatusChip
                      label={detailIncident.sla_breach ? 'Breached' : 'On Track'}
                      tone={detailIncident.sla_breach ? 'breached' : 'on_track'}
                    />
                  </div>
                  <div className="form-field">
                    <label>OLA target</label>
                    <div>{detailIncident.ola_target_minutes ? `${detailIncident.ola_target_minutes} minutes` : 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>UC target</label>
                    <div>{detailIncident.uc_target_minutes ? `${detailIncident.uc_target_minutes} minutes` : 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>OLA due</label>
                    <div>{formatDate(detailIncident.ola_due_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>OLA breach</label>
                    <StatusChip
                      label={detailIncident.ola_breach ? 'Breached' : 'On Track'}
                      tone={detailIncident.ola_breach ? 'breached' : 'on_track'}
                    />
                  </div>
                  <div className="form-field">
                    <label>UC due</label>
                    <div>{formatDate(detailIncident.uc_due_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>UC breach</label>
                    <StatusChip
                      label={detailIncident.uc_breach ? 'Breached' : 'On Track'}
                      tone={detailIncident.uc_breach ? 'breached' : 'on_track'}
                    />
                  </div>
                  <div className="form-field">
                    <label>First response</label>
                    <div>{formatDate(detailIncident.first_response_time)}</div>
                  </div>
                  <div className="form-field">
                    <label>Resolved at</label>
                    <div>{formatDate(detailIncident.resolved_at)}</div>
                  </div>
                  <div className="form-field">
                    <label>Closed at</label>
                    <div>{formatDate(detailIncident.closed_at)}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Major incident workflow</label>
                    {majorError && <div className="banner">{majorError}</div>}
                    {usersError && <div className="banner">{usersError}</div>}
                    {majorMissingFields && (
                      <div className="banner">Required: major level, manager, and cadence.</div>
                    )}
                    <div className="form-grid">
                      <div className="form-field">
                        <label>Major incident</label>
                        <select
                          value={majorForm.isMajor}
                          onChange={(event) => setMajorForm((prev) => ({
                            ...prev,
                            isMajor: event.target.value,
                          }))}
                        >
                          <option value="no">No</option>
                          <option value="yes">Yes</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>Major level</label>
                        <select
                          value={majorForm.level}
                          onChange={(event) => setMajorForm((prev) => ({
                            ...prev,
                            level: event.target.value,
                          }))}
                          disabled={majorForm.isMajor !== 'yes'}
                        >
                          <option value="">Select level</option>
                          <option value="mi1">Major 1 (Critical)</option>
                          <option value="mi2">Major 2 (High)</option>
                          <option value="mi3">Major 3 (Medium)</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>Escalation status</label>
                        <select
                          value={majorForm.escalationStatus}
                          onChange={(event) => setMajorForm((prev) => ({
                            ...prev,
                            escalationStatus: event.target.value,
                          }))}
                        >
                          <option value="not_escalated">Not escalated</option>
                          <option value="escalated">Escalated</option>
                          <option value="de_escalated">De-escalated</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>Major incident manager</label>
                        <select
                          value={majorForm.managerId}
                          onChange={(event) => setMajorForm((prev) => ({
                            ...prev,
                            managerId: event.target.value,
                          }))}
                        >
                          <option value="">Unassigned</option>
                          {usersLoading ? (
                            <option value="">Loading users...</option>
                          ) : (
                            users.map((user) => (
                              <option key={user.id} value={user.id}>
                                {user.full_name || user.email}
                              </option>
                            ))
                          )}
                        </select>
                      </div>
                      <div className="form-field">
                        <label>Communication cadence (minutes)</label>
                        <input
                          type="number"
                          min="1"
                          value={majorForm.cadenceMinutes}
                          onChange={(event) => setMajorForm((prev) => ({
                            ...prev,
                            cadenceMinutes: event.target.value,
                          }))}
                          disabled={majorForm.isMajor !== 'yes'}
                        />
                      </div>
                    </div>
                    <button type="button" onClick={handleMajorUpdate} disabled={majorSubmitting || majorMissingFields}>
                      {majorSubmitting ? 'Saving...' : 'Save major workflow'}
                    </button>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Communications</label>
                    {commError && <div className="banner">{commError}</div>}
                    <div className="form-grid">
                      <div className="form-field">
                        <label>Channel</label>
                        <select
                          value={commForm.channel}
                          onChange={(event) => setCommForm((prev) => ({
                            ...prev,
                            channel: event.target.value,
                          }))}
                        >
                          <option value="email">Email</option>
                          <option value="sms">SMS</option>
                          <option value="portal">Portal</option>
                          <option value="chat">Chat</option>
                          <option value="call">Call</option>
                          <option value="meeting">Meeting</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>Audience</label>
                        <select
                          value={commForm.audience}
                          onChange={(event) => setCommForm((prev) => ({
                            ...prev,
                            audience: event.target.value,
                          }))}
                        >
                          <option value="internal">Internal</option>
                          <option value="external">External</option>
                          <option value="executive">Executive</option>
                        </select>
                      </div>
                      <div className="form-field form-field-full">
                        <label>Message</label>
                        <textarea
                          rows={3}
                          value={commForm.message}
                          onChange={(event) => setCommForm((prev) => ({
                            ...prev,
                            message: event.target.value,
                          }))}
                          placeholder="Share the latest update"
                        />
                      </div>
                    </div>
                    <button type="button" onClick={handleCommunicationSubmit} disabled={commSubmitting}>
                      {commSubmitting ? 'Sending...' : 'Add communication'}
                    </button>
                    {Array.isArray(detailIncident.communications) && detailIncident.communications.length > 0 ? (
                      <div className="muted" style={{ marginTop: '0.75rem' }}>
                        {detailIncident.communications.map((comm) => (
                          <div key={comm.id}>
                            {formatDate(comm.sent_at)} - {comm.channel} - {comm.audience} - {comm.message}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted" style={{ marginTop: '0.75rem' }}>No communications logged yet.</div>
                    )}
                  </div>
                  <div className="form-field form-field-full">
                    <label>Post-incident review</label>
                    {pirError && <div className="banner">{pirError}</div>}
                    {pirMissingFields && (
                      <div className="banner">Required: owner and summary when PIR is required.</div>
                    )}
                    <div className="form-grid">
                      <div className="form-field">
                        <label>PIR required</label>
                        <select
                          value={pirForm.required}
                          onChange={(event) => setPirForm((prev) => ({
                            ...prev,
                            required: event.target.value,
                            status: event.target.value === 'yes' ? prev.status : 'not_required',
                          }))}
                        >
                          <option value="no">No</option>
                          <option value="yes">Yes</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>PIR status</label>
                        <select
                          value={pirForm.status}
                          onChange={(event) => setPirForm((prev) => ({
                            ...prev,
                            status: event.target.value,
                          }))}
                          disabled={pirForm.required !== 'yes'}
                        >
                          <option value="pending">Pending</option>
                          <option value="in_review">In Review</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>
                      <div className="form-field">
                        <label>PIR owner</label>
                        <select
                          value={pirForm.ownerId}
                          onChange={(event) => setPirForm((prev) => ({
                            ...prev,
                            ownerId: event.target.value,
                          }))}
                        >
                          <option value="">Unassigned</option>
                          {usersLoading ? (
                            <option value="">Loading users...</option>
                          ) : (
                            users.map((user) => (
                              <option key={user.id} value={user.id}>
                                {user.full_name || user.email}
                              </option>
                            ))
                          )}
                        </select>
                      </div>
                      <div className="form-field form-field-full">
                        <label>PIR summary</label>
                        <input
                          value={pirForm.summary}
                          onChange={(event) => setPirForm((prev) => ({
                            ...prev,
                            summary: event.target.value,
                          }))}
                          placeholder="Root cause and key resolution summary"
                        />
                      </div>
                      <div className="form-field form-field-full">
                        <label>PIR notes</label>
                        <textarea
                          rows={3}
                          value={pirForm.notes}
                          onChange={(event) => setPirForm((prev) => ({
                            ...prev,
                            notes: event.target.value,
                          }))}
                          placeholder="Lessons learned and follow-up actions"
                        />
                      </div>
                      <div className="form-field">
                        <label>PIR completed</label>
                        <div>{formatDate(detailIncident.pir_completed_at)}</div>
                      </div>
                    </div>
                    <button type="button" onClick={handlePirUpdate} disabled={pirSubmitting || pirMissingFields}>
                      {pirSubmitting ? 'Saving...' : 'Save PIR'}
                    </button>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Recent communications</label>
                    {Array.isArray(detailIncident.communications) && detailIncident.communications.length > 0 ? (
                      <div className="muted">
                        {detailIncident.communications.slice(0, 5).map((comm) => (
                          <div key={comm.id}>
                            {formatDate(comm.sent_at)} - {comm.channel} - {comm.audience} - {comm.message}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No communications logged yet.</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
