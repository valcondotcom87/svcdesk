import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import ModuleCategoryPanel from '../components/ModuleCategoryPanel.jsx'
import { apiRequest } from '../api/client.js'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'problem', label: 'Problem' },
  { key: 'summary', label: 'Summary' },
  { key: 'status', label: 'Status' },
  { key: 'linked', label: 'Linked Incidents' },
  { key: 'owner', label: 'Owner' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['resolved', 'closed'].includes(value)) return 'green'
  if (['investigating', 'diagnosed'].includes(value)) return 'amber'
  if (['solution_identified'].includes(value)) return 'blue'
  return 'blue'
}

export default function Problems({ onCreateTicket }) {
  const navigate = useNavigate()
  const [categoryFilter, setCategoryFilter] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailProblem, setDetailProblem] = useState(null)
  const [selectedProblemId, setSelectedProblemId] = useState(null)
  const [resolutionForm, setResolutionForm] = useState({
    status: 'identified',
    rootCause: '',
    workaround: '',
    permanentSolution: '',
  })
  const [resolutionSubmitting, setResolutionSubmitting] = useState(false)
  const [resolutionError, setResolutionError] = useState('')
  const [rcaForm, setRcaForm] = useState({
    investigationMethod: '',
    fiveWhys: '',
    contributingFactors: '',
    lessonsLearned: '',
  })
  const [rcaSubmitting, setRcaSubmitting] = useState(false)
  const [rcaError, setRcaError] = useState('')
  const [kedbForm, setKedbForm] = useState({
    title: '',
    description: '',
    errorCode: '',
    symptoms: '',
    workaround: '',
    permanentSolution: '',
  })
  const [kedbSubmitting, setKedbSubmitting] = useState(false)
  const [kedbError, setKedbError] = useState('')
  const { data: categoryData } = useApi('/organizations/module-categories/?module=problems&is_active=true&ordering=sort_order&page_size=200')
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const categoryQuery = categoryFilter ? `&category=${encodeURIComponent(categoryFilter)}` : ''
  const { data, isLoading, reload } = useApi(`/problems/problems/?ordering=-created_at&page_size=10${categoryQuery}`)
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const hasFilter = Boolean(categoryFilter)
  const rows = list.map((item) => ({
    id: item.id,
    problem: item.problem_number || item.ticket_number || 'PRB-00000',
    summary: item.title,
    status: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    linked: item.related_incident_count ?? '0',
    owner: item.owner_name || 'Unassigned',
  }))

  const formatDate = (value) => {
    if (!value) return 'N/A'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toLocaleString()
  }

  const openDetail = (problemId) => {
    if (!problemId) return
    setSelectedProblemId(problemId)
    setDetailOpen(true)
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailProblem(null)
    setDetailError('')
    setResolutionError('')
    setRcaError('')
    setKedbError('')
  }

  const loadDetail = (problemId) => {
    if (!problemId) return
    setDetailLoading(true)
    setDetailError('')
    apiRequest(`/problems/problems/${problemId}/`)
      .then((payload) => {
        setDetailProblem(payload)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load problem details.'
        setDetailError(message)
      })
      .finally(() => {
        setDetailLoading(false)
      })
  }

  useEffect(() => {
    const handler = (event) => {
      if (event?.detail?.type === 'problem') {
        reload()
      }
    }
    window.addEventListener('itsm:ticket-created', handler)
    return () => window.removeEventListener('itsm:ticket-created', handler)
  }, [reload])

  useEffect(() => {
    if (!detailOpen || !selectedProblemId) return
    loadDetail(selectedProblemId)
  }, [detailOpen, selectedProblemId])

  useEffect(() => {
    if (!detailProblem) return
    setResolutionForm({
      status: detailProblem.status || 'identified',
      rootCause: detailProblem.root_cause || '',
      workaround: detailProblem.workaround || '',
      permanentSolution: detailProblem.permanent_solution || '',
    })
    setRcaForm({
      investigationMethod: detailProblem.rca?.investigation_method || '',
      fiveWhys: detailProblem.rca?.five_whys || '',
      contributingFactors: detailProblem.rca?.contributing_factors || '',
      lessonsLearned: detailProblem.rca?.lessons_learned || '',
    })
    setKedbForm({
      title: detailProblem.kedb_entry?.title || detailProblem.title || '',
      description: detailProblem.kedb_entry?.description || detailProblem.description || '',
      errorCode: detailProblem.kedb_entry?.error_code || `KEDB-${detailProblem.ticket_number || ''}`,
      symptoms: detailProblem.kedb_entry?.symptoms || '',
      workaround: detailProblem.kedb_entry?.workaround || detailProblem.workaround || '',
      permanentSolution: detailProblem.kedb_entry?.permanent_solution || detailProblem.permanent_solution || '',
    })
    setResolutionError('')
    setRcaError('')
    setKedbError('')
  }, [detailProblem])

  const resolutionNeedsRca = ['resolved', 'closed'].includes(resolutionForm.status)
  const resolutionMissingFields = resolutionNeedsRca
    && (!resolutionForm.rootCause.trim() || !resolutionForm.permanentSolution.trim() || !detailProblem?.rca)

  const handleResolutionUpdate = async () => {
    if (!detailProblem?.id || resolutionSubmitting) return
    if (resolutionMissingFields) {
      setResolutionError('Resolution requires root cause, permanent solution, and RCA record.')
      return
    }
    setResolutionSubmitting(true)
    setResolutionError('')
    try {
      await apiRequest(`/problems/problems/${detailProblem.id}/`, {
        method: 'PATCH',
        body: {
          status: resolutionForm.status,
          root_cause: resolutionForm.rootCause.trim(),
          workaround: resolutionForm.workaround.trim(),
          permanent_solution: resolutionForm.permanentSolution.trim(),
        },
      })
      reload()
      loadDetail(detailProblem.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to update problem resolution.'
      setResolutionError(message)
    } finally {
      setResolutionSubmitting(false)
    }
  }

  const handleAddRca = async () => {
    if (!detailProblem?.id || rcaSubmitting) return
    const hasInput = Object.values(rcaForm).some((value) => String(value).trim())
    if (!hasInput) {
      setRcaError('Add at least one RCA field before saving.')
      return
    }
    setRcaSubmitting(true)
    setRcaError('')
    try {
      await apiRequest(`/problems/problems/${detailProblem.id}/add_rca/`, {
        method: 'POST',
        body: {
          investigation_method: rcaForm.investigationMethod.trim(),
          five_whys: rcaForm.fiveWhys.trim(),
          contributing_factors: rcaForm.contributingFactors.trim(),
          lessons_learned: rcaForm.lessonsLearned.trim(),
        },
      })
      reload()
      loadDetail(detailProblem.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to add RCA.'
      setRcaError(message)
    } finally {
      setRcaSubmitting(false)
    }
  }

  const kedbMissingFields = !kedbForm.title.trim()
    || !kedbForm.description.trim()
    || !kedbForm.errorCode.trim()
    || !kedbForm.symptoms.trim()
    || !kedbForm.workaround.trim()

  const handleAddKedb = async () => {
    if (!detailProblem?.id || kedbSubmitting) return
    if (kedbMissingFields) {
      setKedbError('KEDB requires title, description, error code, symptoms, and workaround.')
      return
    }
    setKedbSubmitting(true)
    setKedbError('')
    try {
      await apiRequest(`/problems/problems/${detailProblem.id}/add_kedb/`, {
        method: 'POST',
        body: {
          title: kedbForm.title.trim(),
          description: kedbForm.description.trim(),
          error_code: kedbForm.errorCode.trim(),
          symptoms: kedbForm.symptoms.trim(),
          workaround: kedbForm.workaround.trim(),
          permanent_solution: kedbForm.permanentSolution.trim(),
        },
      })
      reload()
      loadDetail(detailProblem.id)
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to add known error entry.'
      setKedbError(message)
    } finally {
      setKedbSubmitting(false)
    }
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Problem Management"
        subtitle="Root cause analysis, known errors, and long-term fixes"
        actions={(
          <button type="button" onClick={() => onCreateTicket?.('problem')}>
            New Problem
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
          <strong>{hasFilter ? 'No problems match this category' : 'No problem records yet'}</strong>
          <div className="muted">
            {hasFilter
              ? 'Clear the filter or try another category to see problems.'
              : 'Log recurring issues to drive RCA and known error tracking.'}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            {hasFilter ? (
              <button type="button" onClick={() => setCategoryFilter('')}>Clear filter</button>
            ) : (
              <button type="button" onClick={() => navigate('/knowledge')}>Search Knowledge</button>
            )}
            <button type="button" className="ghost" onClick={() => onCreateTicket?.('problem')}>
              New Problem
            </button>
          </div>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No problems found."
        onRowClick={(row) => openDetail(row.id)}
      />
      <ModuleCategoryPanel moduleKey="problems" title="Problem Categories" />

      {detailOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Problem detail"
            style={{ maxWidth: '760px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Problem Detail</h2>
                <p className="muted">RCA, known errors, and resolution lifecycle.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading problem details...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailProblem && (
                <div className="form-grid">
                  <div className="form-field">
                    <label>Ticket</label>
                    <div>{detailProblem.ticket_number}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailProblem.status_display || detailProblem.status}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Title</label>
                    <div>{detailProblem.title}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Description</label>
                    <div>{detailProblem.description}</div>
                  </div>
                  <div className="form-field">
                    <label>Category</label>
                    <div>{detailProblem.category || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Owner</label>
                    <div>{detailProblem.owner_name || 'Unassigned'}</div>
                  </div>
                  <div className="form-field">
                    <label>Identified</label>
                    <div>{formatDate(detailProblem.identified_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>First incident</label>
                    <div>{formatDate(detailProblem.first_incident_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>Resolved</label>
                    <div>{formatDate(detailProblem.resolved_date)}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Root cause analysis</label>
                    {detailProblem.rca ? (
                      <div className="muted">
                        <div><strong>Method:</strong> {detailProblem.rca.investigation_method || 'N/A'}</div>
                        <div><strong>Five whys:</strong> {detailProblem.rca.five_whys || 'N/A'}</div>
                        <div><strong>Contributing factors:</strong> {detailProblem.rca.contributing_factors || 'N/A'}</div>
                        <div><strong>Lessons learned:</strong> {detailProblem.rca.lessons_learned || 'N/A'}</div>
                      </div>
                    ) : (
                      <div className="muted">No RCA recorded yet.</div>
                    )}
                  </div>
                  {!detailProblem.rca && (
                    <div className="form-field form-field-full">
                      <label>Add RCA</label>
                      {rcaError && <div className="banner">{rcaError}</div>}
                      <div className="form-grid">
                        <div className="form-field">
                          <label>Investigation method</label>
                          <input
                            value={rcaForm.investigationMethod}
                            onChange={(event) => setRcaForm((prev) => ({
                              ...prev,
                              investigationMethod: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field">
                          <label>Five whys</label>
                          <input
                            value={rcaForm.fiveWhys}
                            onChange={(event) => setRcaForm((prev) => ({
                              ...prev,
                              fiveWhys: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Contributing factors</label>
                          <textarea
                            rows={3}
                            value={rcaForm.contributingFactors}
                            onChange={(event) => setRcaForm((prev) => ({
                              ...prev,
                              contributingFactors: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Lessons learned</label>
                          <textarea
                            rows={3}
                            value={rcaForm.lessonsLearned}
                            onChange={(event) => setRcaForm((prev) => ({
                              ...prev,
                              lessonsLearned: event.target.value,
                            }))}
                          />
                        </div>
                      </div>
                      <button type="button" onClick={handleAddRca} disabled={rcaSubmitting}>
                        {rcaSubmitting ? 'Saving...' : 'Save RCA'}
                      </button>
                    </div>
                  )}
                  <div className="form-field form-field-full">
                    <label>Known error entry</label>
                    {detailProblem.kedb_entry ? (
                      <div className="muted">
                        <div><strong>Error code:</strong> {detailProblem.kedb_entry.error_code}</div>
                        <div><strong>Symptoms:</strong> {detailProblem.kedb_entry.symptoms}</div>
                        <div><strong>Workaround:</strong> {detailProblem.kedb_entry.workaround}</div>
                        <div><strong>Permanent solution:</strong> {detailProblem.kedb_entry.permanent_solution || 'N/A'}</div>
                      </div>
                    ) : (
                      <div className="muted">No known error entry yet.</div>
                    )}
                  </div>
                  {!detailProblem.kedb_entry && (
                    <div className="form-field form-field-full">
                      <label>Add Known Error (KEDB)</label>
                      {kedbError && <div className="banner">{kedbError}</div>}
                      {kedbMissingFields && (
                        <div className="banner">Required: title, description, error code, symptoms, and workaround.</div>
                      )}
                      <div className="form-grid">
                        <div className="form-field">
                          <label>Title</label>
                          <input
                            value={kedbForm.title}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              title: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field">
                          <label>Error code</label>
                          <input
                            value={kedbForm.errorCode}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              errorCode: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Description</label>
                          <textarea
                            rows={3}
                            value={kedbForm.description}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              description: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Symptoms</label>
                          <textarea
                            rows={3}
                            value={kedbForm.symptoms}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              symptoms: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Workaround</label>
                          <textarea
                            rows={3}
                            value={kedbForm.workaround}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              workaround: event.target.value,
                            }))}
                          />
                        </div>
                        <div className="form-field form-field-full">
                          <label>Permanent solution</label>
                          <textarea
                            rows={3}
                            value={kedbForm.permanentSolution}
                            onChange={(event) => setKedbForm((prev) => ({
                              ...prev,
                              permanentSolution: event.target.value,
                            }))}
                          />
                        </div>
                      </div>
                      <button type="button" onClick={handleAddKedb} disabled={kedbSubmitting || kedbMissingFields}>
                        {kedbSubmitting ? 'Saving...' : 'Save KEDB Entry'}
                      </button>
                    </div>
                  )}
                  <div className="form-field form-field-full">
                    <label>Resolution & status</label>
                    {resolutionError && <div className="banner">{resolutionError}</div>}
                    {resolutionMissingFields && (
                      <div className="banner">Resolution requires root cause, permanent solution, and RCA.</div>
                    )}
                    <div className="form-grid">
                      <div className="form-field">
                        <label>Status</label>
                        <select
                          value={resolutionForm.status}
                          onChange={(event) => setResolutionForm((prev) => ({
                            ...prev,
                            status: event.target.value,
                          }))}
                        >
                          <option value="identified">Identified</option>
                          <option value="investigating">Investigating</option>
                          <option value="diagnosed">Diagnosed</option>
                          <option value="solution_identified">Solution Identified</option>
                          <option value="resolved">Resolved</option>
                          <option value="closed">Closed</option>
                        </select>
                      </div>
                      <div className="form-field form-field-full">
                        <label>Root cause</label>
                        <textarea
                          rows={3}
                          value={resolutionForm.rootCause}
                          onChange={(event) => setResolutionForm((prev) => ({
                            ...prev,
                            rootCause: event.target.value,
                          }))}
                        />
                      </div>
                      <div className="form-field form-field-full">
                        <label>Workaround</label>
                        <textarea
                          rows={3}
                          value={resolutionForm.workaround}
                          onChange={(event) => setResolutionForm((prev) => ({
                            ...prev,
                            workaround: event.target.value,
                          }))}
                        />
                      </div>
                      <div className="form-field form-field-full">
                        <label>Permanent solution</label>
                        <textarea
                          rows={3}
                          value={resolutionForm.permanentSolution}
                          onChange={(event) => setResolutionForm((prev) => ({
                            ...prev,
                            permanentSolution: event.target.value,
                          }))}
                        />
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={handleResolutionUpdate}
                      disabled={resolutionSubmitting || resolutionMissingFields}
                    >
                      {resolutionSubmitting ? 'Saving...' : 'Save Status & Resolution'}
                    </button>
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
