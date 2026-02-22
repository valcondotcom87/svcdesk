import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import { useApi } from '../api/hooks.js'
import { apiRequest, getToken } from '../api/client'
import { getCurrentUser } from '../api/auth.js'

const columns = [
  { key: 'article', label: 'Article' },
  { key: 'category', label: 'Category' },
  { key: 'status', label: 'Status' },
  { key: 'owner', label: 'Owner' },
  { key: 'updated', label: 'Updated' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (value === 'published') return 'green'
  if (value === 'review') return 'amber'
  if (value === 'archived') return 'red'
  return 'blue'
}

export default function Knowledge() {
  const navigate = useNavigate()
  const { data, isLoading, reload } = useApi('/knowledge/articles/?ordering=-updated_at&page_size=10')
  const [showForm, setShowForm] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailArticle, setDetailArticle] = useState(null)
  const [selectedArticleId, setSelectedArticleId] = useState(null)
  const [actionNotes, setActionNotes] = useState('')
  const [formState, setFormState] = useState({
    title: '',
    summary: '',
    content: '',
    category: '',
    status: 'draft',
    tags: '',
    csfFunction: 'identify',
    csfCategory: '',
    isoControl: '',
    nistControl: '',
  })
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const rows = list.map((item) => ({
    id: item.id,
    article: item.title,
    category: item.category || 'General',
    status: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    owner: item.owner_name || 'Unassigned',
    updated: item.updated_at ? new Date(item.updated_at).toLocaleDateString() : 'N/A',
  }))

  const currentUser = getCurrentUser()
  const isEndUser = currentUser?.role === 'end_user'

  const publishChecklist = detailArticle
    ? [
        { label: 'Summary added', ok: Boolean(detailArticle.summary?.trim()) },
        { label: 'Category assigned', ok: Boolean(detailArticle.category?.trim()) },
        { label: 'Tags added', ok: Boolean(detailArticle.tags?.trim()) },
        { label: 'CSF function set', ok: Boolean(detailArticle.csf_function?.trim()) },
        { label: 'ISO control set', ok: Boolean(detailArticle.iso_control?.trim()) },
        { label: 'NIST control set', ok: Boolean(detailArticle.nist_control?.trim()) },
      ]
    : []
  const publishReady = publishChecklist.every((item) => item.ok)

  const openDetail = (articleId) => {
    if (!articleId) return
    setSelectedArticleId(articleId)
    setDetailOpen(true)
    setDetailError('')
    setDetailLoading(true)
    apiRequest(`/knowledge/articles/${articleId}/`)
      .then((payload) => {
        setDetailArticle(payload)
        setActionNotes(payload?.review_notes || '')
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load article.'
        setDetailError(message)
      })
      .finally(() => setDetailLoading(false))
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailArticle(null)
    setDetailError('')
    setActionNotes('')
  }

  const handleLifecycleAction = async (action) => {
    if (!detailArticle) return
    setDetailError('')
    try {
      await apiRequest(`/knowledge/articles/${detailArticle.id}/${action}/`, {
        method: 'POST',
        body: actionNotes.trim() ? { notes: actionNotes.trim() } : undefined,
      })
      closeDetail()
      reload()
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Action failed.'
      setDetailError(message)
    }
  }

  const handleChange = (field) => (event) => {
    setFormState((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const handleCreate = async (event) => {
    event.preventDefault()
    setError('')

    if (!getToken()) {
      setError('Please sign in before creating an article.')
      return
    }

    if (!formState.title.trim() || !formState.content.trim()) {
      setError('Title and content are required.')
      return
    }

    setIsSubmitting(true)
    try {
      const currentUser = getCurrentUser()
      await apiRequest('/knowledge/articles/', {
        method: 'POST',
        body: {
          title: formState.title.trim(),
          summary: formState.summary.trim(),
          content: formState.content.trim(),
          category: formState.category.trim(),
          status: formState.status,
          owner: currentUser?.id || null,
          tags: formState.tags.trim(),
          csf_function: formState.csfFunction,
          csf_category: formState.csfCategory.trim(),
          iso_control: formState.isoControl.trim(),
          nist_control: formState.nistControl.trim(),
        },
      })
      setShowForm(false)
      setFormState({
        title: '',
        summary: '',
        content: '',
        category: '',
        status: 'draft',
        tags: '',
        csfFunction: 'identify',
        csfCategory: '',
        isoControl: '',
        nistControl: '',
      })
      reload()
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to create article.'
      setError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Knowledge Management"
        subtitle="Articles, approvals, and feedback"
        actions={<button type="button" onClick={() => setShowForm(true)}>New Article</button>}
      />
      {isEndUser ? (
        <div className="banner" style={{ marginBottom: '1rem' }}>
          <strong>Find a fix fast</strong>
          <div className="muted">Search for known solutions before creating a request.</div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginTop: '0.5rem' }}>
            <button type="button" onClick={() => navigate('/requests')}>Go to Requests</button>
            <button type="button" className="ghost" onClick={() => navigate('/incidents')}>Report Incident</button>
          </div>
        </div>
      ) : null}
      {!isLoading && rows.length === 0 ? (
        <div className="banner" style={{ marginBottom: '1rem' }}>
          <strong>No articles yet</strong>
          <div className="muted">Create the first article to help end users solve common issues.</div>
        </div>
      ) : null}
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No knowledge articles found."
        onRowClick={(row) => openDetail(row.id)}
      />

      {detailOpen ? (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Knowledge article detail"
            style={{ maxWidth: '760px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Knowledge Article</h2>
                <p className="muted">Lifecycle, ownership, and content review.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading article...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailArticle ? (
                <div className="form-grid">
                  <div className="form-field form-field-full">
                    <label>Title</label>
                    <div>{detailArticle.title}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailArticle.status_display || detailArticle.status}</div>
                  </div>
                  <div className="form-field">
                    <label>Owner</label>
                    <div>{detailArticle.owner_name || 'Unassigned'}</div>
                  </div>
                  <div className="form-field">
                    <label>Category</label>
                    <div>{detailArticle.category || 'General'}</div>
                  </div>
                  <div className="form-field">
                    <label>Version</label>
                    <div>{detailArticle.version}</div>
                  </div>
                  <div className="form-field">
                    <label>Published</label>
                    <div>{detailArticle.published_at ? new Date(detailArticle.published_at).toLocaleString() : 'Not published'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Summary</label>
                    <div>{detailArticle.summary || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Content</label>
                    <div style={{ whiteSpace: 'pre-wrap' }}>{detailArticle.content}</div>
                  </div>
                  <div className="form-field">
                    <label>NIST CSF Function</label>
                    <div>{detailArticle.csf_function}</div>
                  </div>
                  <div className="form-field">
                    <label>ISO Control</label>
                    <div>{detailArticle.iso_control || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Tags</label>
                    <div>{detailArticle.tags || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Review Notes</label>
                    <div>{detailArticle.review_notes || 'N/A'}</div>
                  </div>
                </div>
              ) : null}
            </div>
            {detailArticle ? (
              <div className="modal-actions">
                <div className="form-field" style={{ flex: 1 }}>
                  <label htmlFor="kb-action-notes">Approval note (optional)</label>
                  <input
                    id="kb-action-notes"
                    value={actionNotes}
                    onChange={(event) => setActionNotes(event.target.value)}
                    placeholder="Reason, reviewer feedback, or approval notes"
                  />
                </div>
                {detailArticle.status === 'draft' || detailArticle.status === 'archived' ? (
                  <button type="button" onClick={() => handleLifecycleAction('submit_review')}>Submit for Review</button>
                ) : null}
                {detailArticle.status === 'review' ? (
                  <button type="button" onClick={() => handleLifecycleAction('publish')} disabled={!publishReady}>
                    Publish
                  </button>
                ) : null}
                {detailArticle.status === 'published' ? (
                  <button type="button" className="ghost" onClick={() => handleLifecycleAction('archive')}>Archive</button>
                ) : null}
              </div>
            ) : null}
          </div>
        </div>
      ) : null}
      {detailArticle && detailArticle.status === 'review' ? (
        <div className="card" style={{ marginTop: '1rem' }}>
          <div className="card-header">
            <h3>Publish checklist</h3>
            <p className="muted">All items must be complete before publishing.</p>
          </div>
          <div className="card-body">
            {publishChecklist.map((item) => (
              <div key={item.label} style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>{item.label}</span>
                <strong>{item.ok ? 'OK' : 'Missing'}</strong>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      {showForm ? (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Create knowledge article"
            style={{ maxHeight: '90vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Create Knowledge Article</h2>
                <p className="muted">Capture a reusable solution or guide.</p>
              </div>
              <button type="button" className="ghost" onClick={() => setShowForm(false)}>Close</button>
            </div>
            <form
              className="modal-body"
              onSubmit={handleCreate}
              style={{ overflowY: 'auto', paddingRight: '0.5rem' }}
            >
              {!getToken() ? (
                <div className="banner">
                  <div>
                    <strong>Sign in required</strong>
                    <div className="muted">Please sign in before creating an article.</div>
                  </div>
                </div>
              ) : null}

              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="kb-title">Title</label>
                  <input
                    id="kb-title"
                    value={formState.title}
                    onChange={handleChange('title')}
                    placeholder="Short, descriptive title"
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="kb-category">Category (optional)</label>
                  <input
                    id="kb-category"
                    value={formState.category}
                    onChange={handleChange('category')}
                    placeholder="Network, Software, Security"
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="kb-summary">Summary (optional)</label>
                  <textarea
                    id="kb-summary"
                    value={formState.summary}
                    onChange={handleChange('summary')}
                    placeholder="Short overview"
                    rows={2}
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="kb-content">Content</label>
                  <textarea
                    id="kb-content"
                    value={formState.content}
                    onChange={handleChange('content')}
                    placeholder="Steps, details, and resolution"
                    rows={6}
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="kb-status">Status</label>
                  <select id="kb-status" value={formState.status} onChange={handleChange('status')}>
                    <option value="draft">Draft</option>
                    <option value="review">Review</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="kb-tags">Tags (optional)</label>
                  <input
                    id="kb-tags"
                    value={formState.tags}
                    onChange={handleChange('tags')}
                    placeholder="vpn, onboarding, printer"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="kb-csf">NIST CSF Function</label>
                  <select id="kb-csf" value={formState.csfFunction} onChange={handleChange('csfFunction')}>
                    <option value="govern">Govern</option>
                    <option value="identify">Identify</option>
                    <option value="protect">Protect</option>
                    <option value="detect">Detect</option>
                    <option value="respond">Respond</option>
                    <option value="recover">Recover</option>
                  </select>
                  <div className="muted">Required before publishing.</div>
                </div>
                <div className="form-field">
                  <label htmlFor="kb-csf-category">NIST CSF Category (optional)</label>
                  <input
                    id="kb-csf-category"
                    value={formState.csfCategory}
                    onChange={handleChange('csfCategory')}
                    placeholder="ID.AM, PR.AC, DE.CM"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="kb-iso-control">ISO 27001 Control (optional)</label>
                  <input
                    id="kb-iso-control"
                    value={formState.isoControl}
                    onChange={handleChange('isoControl')}
                    placeholder="A.5.1, A.8.1"
                  />
                  <div className="muted">Required before publishing.</div>
                </div>
                <div className="form-field">
                  <label htmlFor="kb-nist-control">NIST Control (optional)</label>
                  <input
                    id="kb-nist-control"
                    value={formState.nistControl}
                    onChange={handleChange('nistControl')}
                    placeholder="AC-1, SI-2"
                  />
                  <div className="muted">Required before publishing.</div>
                </div>
              </div>

              {error ? <div className="form-error">{error}</div> : null}

              <div className="modal-actions">
                <button type="button" className="ghost" onClick={() => setShowForm(false)}>Cancel</button>
                <button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? 'Creating...' : 'Create Article'}
                </button>
              </div>
            </form>
          </div>
        </div>
      ) : null}
    </div>
  )
}
