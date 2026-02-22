import { useEffect, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import DataTable from '../components/DataTable.jsx'
import StatusChip from '../components/StatusChip.jsx'
import { apiRequest } from '../api/client.js'
import { useApi } from '../api/hooks.js'

const columns = [
  { key: 'ci', label: 'CI' },
  { key: 'type', label: 'Type' },
  { key: 'status', label: 'Status' },
  { key: 'owner', label: 'Owner' },
  { key: 'location', label: 'Location' },
]

const relationshipOptions = [
  { value: 'depends_on', label: 'Depends On' },
  { value: 'supports', label: 'Supports' },
  { value: 'connected_to', label: 'Connected To' },
  { value: 'part_of', label: 'Part Of' },
  { value: 'used_by', label: 'Used By' },
  { value: 'installed_on', label: 'Installed On' },
]

const statusTone = (status) => {
  const value = String(status || '').toLowerCase()
  if (['active'].includes(value)) return 'green'
  if (['inactive', 'pending'].includes(value)) return 'amber'
  if (['retired'].includes(value)) return 'red'
  return 'blue'
}

export default function CMDB() {
  const [createOpen, setCreateOpen] = useState(false)
  const [createSubmitting, setCreateSubmitting] = useState(false)
  const [createError, setCreateError] = useState('')
  const [formState, setFormState] = useState({
    ciNumber: '',
    name: '',
    description: '',
    categoryId: '',
    ciClass: 'service',
    type: '',
    status: 'active',
    lifecycleStage: 'in_operation',
    criticality: 'medium',
    verificationStatus: 'unverified',
    ownerTeamId: '',
    location: '',
    version: '',
    manufacturer: '',
    serialNumber: '',
    acquisitionDate: '',
    warrantyExpiry: '',
    disposalDate: '',
    impactAnalysis: '',
    relationshipTargetId: '',
    relationshipType: '',
  })
  const [detailOpen, setDetailOpen] = useState(false)
  const [detailLoading, setDetailLoading] = useState(false)
  const [detailError, setDetailError] = useState('')
  const [detailCI, setDetailCI] = useState(null)
  const [selectedCiId, setSelectedCiId] = useState(null)
  const { data, isLoading, reload } = useApi('/cmdb/config-items/?ordering=name&page_size=10')
  const { data: relationshipData } = useApi('/cmdb/config-items/?ordering=name&page_size=200')
  const { data: categoryData } = useApi('/cmdb/ci-categories/?ordering=name&page_size=200')
  const { data: teamData } = useApi('/teams/?ordering=name&page_size=200')
  const categories = Array.isArray(categoryData?.results)
    ? categoryData.results
    : Array.isArray(categoryData)
      ? categoryData
      : []
  const teams = Array.isArray(teamData?.results)
    ? teamData.results
    : Array.isArray(teamData)
      ? teamData
      : []
  const relationshipTargets = Array.isArray(relationshipData?.results)
    ? relationshipData.results
    : Array.isArray(relationshipData)
      ? relationshipData
      : []
  const relationshipRequired = relationshipTargets.length > 0
  const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : []
  const rows = list.map((item) => ({
    id: item.id,
    ci: item.ci_number,
    type: item.type || 'CI',
    status: (
      <StatusChip
        label={item.status_display || item.status}
        tone={statusTone(item.status)}
      />
    ),
    owner: item.owner_team_name || 'Unassigned',
    location: item.location || 'N/A',
  }))

  const formatDate = (value) => {
    if (!value) return 'Not set'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return String(value)
    return date.toLocaleString()
  }

  const openDetail = (ciId) => {
    if (!ciId) return
    setSelectedCiId(ciId)
    setDetailOpen(true)
  }

  const closeDetail = () => {
    setDetailOpen(false)
    setDetailCI(null)
    setDetailError('')
  }

  const openCreate = () => {
    setCreateOpen(true)
    setCreateError('')
    setFormState({
      ciNumber: '',
      name: '',
      description: '',
      categoryId: '',
      ciClass: 'service',
      type: '',
      status: 'active',
      lifecycleStage: 'in_operation',
      criticality: 'medium',
      verificationStatus: 'unverified',
      ownerTeamId: '',
      location: '',
      version: '',
      manufacturer: '',
      serialNumber: '',
      acquisitionDate: '',
      warrantyExpiry: '',
      disposalDate: '',
      impactAnalysis: '',
      relationshipTargetId: '',
      relationshipType: '',
    })
  }

  const closeCreate = () => {
    setCreateOpen(false)
    setCreateError('')
  }

  const handleCreateChange = (field) => (event) => {
    setFormState((prev) => ({
      ...prev,
      [field]: event.target.value,
    }))
  }

  const handleCreateSubmit = async (event) => {
    event.preventDefault()
    if (createSubmitting) return
    setCreateSubmitting(true)
    setCreateError('')

    try {
      await apiRequest('/cmdb/config-items/', {
        method: 'POST',
        body: {
          ci_number: formState.ciNumber.trim(),
          name: formState.name.trim(),
          description: formState.description.trim(),
          category: formState.categoryId || null,
          ci_class: formState.ciClass,
          type: formState.type.trim(),
          status: formState.status,
          lifecycle_stage: formState.lifecycleStage,
          criticality: formState.criticality,
          verification_status: formState.verificationStatus,
          owner_team: formState.ownerTeamId || null,
          location: formState.location.trim(),
          version: formState.version.trim(),
          manufacturer: formState.manufacturer.trim(),
          serial_number: formState.serialNumber.trim(),
          acquisition_date: formState.acquisitionDate || null,
          warranty_expiry: formState.warrantyExpiry || null,
          disposal_date: formState.disposalDate || null,
          impact_analysis: formState.impactAnalysis.trim(),
          relationship_target_id: formState.relationshipTargetId || null,
          relationship_type: formState.relationshipType || null,
        },
      })
      setCreateOpen(false)
      reload()
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to create CI.'
      setCreateError(message)
    } finally {
      setCreateSubmitting(false)
    }
  }

  const loadDetail = (ciId) => {
    if (!ciId) return
    setDetailLoading(true)
    setDetailError('')
    apiRequest(`/cmdb/config-items/${ciId}/`)
      .then((payload) => {
        setDetailCI(payload)
      })
      .catch((err) => {
        const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to load CI details.'
        setDetailError(message)
      })
      .finally(() => {
        setDetailLoading(false)
      })
  }

  useEffect(() => {
    if (!detailOpen || !selectedCiId) return
    loadDetail(selectedCiId)
  }, [detailOpen, selectedCiId])

  return (
    <div className="fade-in">
      <PageHeader
        title="CMDB"
        subtitle="Configuration items, relationships, and impact analysis"
        actions={<button type="button" onClick={openCreate}>Add CI</button>}
      />
      <DataTable
        columns={columns}
        rows={rows}
        isLoading={isLoading}
        emptyMessage="No configuration items found."
        onRowClick={(row) => openDetail(row.id)}
      />

      {detailOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="CI detail"
            style={{ maxWidth: '760px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Configuration Item Detail</h2>
                <p className="muted">Classification, ownership, and relationships.</p>
              </div>
              <button type="button" className="ghost" onClick={closeDetail}>Close</button>
            </div>
            <div className="modal-body" style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {detailLoading && <div className="muted">Loading CI details...</div>}
              {detailError && <div className="banner">{detailError}</div>}
              {!detailLoading && detailCI && (
                <div className="form-grid">
                  <div className="form-field">
                    <label>CI Number</label>
                    <div>{detailCI.ci_number}</div>
                  </div>
                  <div className="form-field">
                    <label>Status</label>
                    <div>{detailCI.status_display || detailCI.status}</div>
                  </div>
                  <div className="form-field">
                    <label>CI Class</label>
                    <div>{detailCI.ci_class || 'N/A'}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Name</label>
                    <div>{detailCI.name}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Description</label>
                    <div>{detailCI.description || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Category</label>
                    <div>{detailCI.category_name || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Type</label>
                    <div>{detailCI.type || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Lifecycle Stage</label>
                    <div>{detailCI.lifecycle_stage || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Criticality</label>
                    <div>{detailCI.criticality || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Verification Status</label>
                    <div>{detailCI.verification_status || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Owner Team</label>
                    <div>{detailCI.owner_name || 'Unassigned'}</div>
                  </div>
                  <div className="form-field">
                    <label>Location</label>
                    <div>{detailCI.location || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Version</label>
                    <div>{detailCI.version || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Manufacturer</label>
                    <div>{detailCI.manufacturer || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Serial Number</label>
                    <div>{detailCI.serial_number || 'N/A'}</div>
                  </div>
                  <div className="form-field">
                    <label>Acquisition Date</label>
                    <div>{formatDate(detailCI.acquisition_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>Warranty Expiry</label>
                    <div>{formatDate(detailCI.warranty_expiry)}</div>
                  </div>
                  <div className="form-field">
                    <label>Disposal Date</label>
                    <div>{formatDate(detailCI.disposal_date)}</div>
                  </div>
                  <div className="form-field">
                    <label>Last Verified</label>
                    <div>{formatDate(detailCI.last_verified_at)}</div>
                  </div>
                  <div className="form-field">
                    <label>Last Audit</label>
                    <div>{formatDate(detailCI.last_audit_at)}</div>
                  </div>
                  <div className="form-field form-field-full">
                    <label>Attributes</label>
                    {Array.isArray(detailCI.attributes) && detailCI.attributes.length > 0 ? (
                      <div className="muted">
                        {detailCI.attributes.map((attr) => (
                          <div key={attr.id}>
                            {attr.attribute_name}: {attr.attribute_value}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No attributes recorded.</div>
                    )}
                  </div>
                  <div className="form-field form-field-full">
                    <label>Relationships</label>
                    {Array.isArray(detailCI.related_cis) && detailCI.related_cis.length > 0 ? (
                      <div className="muted">
                        {detailCI.related_cis.map((rel) => (
                          <div key={rel.id}>
                            {rel.source_name} {rel.relationship_type} {rel.target_name}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="muted">No relationships recorded.</div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {createOpen && (
        <div className="modal-overlay" role="presentation">
          <div
            className="modal"
            role="dialog"
            aria-modal="true"
            aria-label="Add configuration item"
            style={{ maxWidth: '760px', maxHeight: '85vh', overflow: 'hidden' }}
          >
            <div className="modal-header">
              <div>
                <h2>Add Configuration Item</h2>
                <p className="muted">Register a CI with ITIL-aligned classification.</p>
              </div>
              <button type="button" className="ghost" onClick={closeCreate}>Close</button>
            </div>
            <form className="modal-body" onSubmit={handleCreateSubmit} style={{ overflowY: 'auto', paddingRight: '0.5rem' }}>
              {createError && <div className="banner">{createError}</div>}
              {!relationshipRequired && (
                <div className="banner">No existing CIs yet. Create the first CI and add relationships later.</div>
              )}
              <div className="form-grid">
                <div className="form-field">
                  <label htmlFor="ci-number">CI Number</label>
                  <input
                    id="ci-number"
                    value={formState.ciNumber}
                    onChange={handleCreateChange('ciNumber')}
                    placeholder="CI-0000"
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-status">Status</label>
                  <select id="ci-status" value={formState.status} onChange={handleCreateChange('status')}>
                    <option value="active">Active</option>
                    <option value="inactive">Inactive</option>
                    <option value="pending">Pending</option>
                    <option value="retired">Retired</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-class">CI Class</label>
                  <select id="ci-class" value={formState.ciClass} onChange={handleCreateChange('ciClass')}>
                    <option value="service">Service</option>
                    <option value="application">Application</option>
                    <option value="infrastructure">Infrastructure</option>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="data">Data</option>
                    <option value="documentation">Documentation</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="ci-name">Name</label>
                  <input
                    id="ci-name"
                    value={formState.name}
                    onChange={handleCreateChange('name')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="ci-description">Description</label>
                  <textarea
                    id="ci-description"
                    rows={3}
                    value={formState.description}
                    onChange={handleCreateChange('description')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-category">Category</label>
                  <select
                    id="ci-category"
                    value={formState.categoryId}
                    onChange={handleCreateChange('categoryId')}
                    required
                  >
                    <option value="">Select category</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-type">Type</label>
                  <input
                    id="ci-type"
                    value={formState.type}
                    onChange={handleCreateChange('type')}
                    placeholder="Hardware, Software, Service"
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-lifecycle">Lifecycle Stage</label>
                  <select id="ci-lifecycle" value={formState.lifecycleStage} onChange={handleCreateChange('lifecycleStage')}>
                    <option value="planned">Planned</option>
                    <option value="design">Design</option>
                    <option value="build">Build</option>
                    <option value="test">Test</option>
                    <option value="in_operation">In Operation</option>
                    <option value="deprecated">Deprecated</option>
                    <option value="retired">Retired</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-criticality">Criticality</label>
                  <select id="ci-criticality" value={formState.criticality} onChange={handleCreateChange('criticality')}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-verification">Verification Status</label>
                  <select id="ci-verification" value={formState.verificationStatus} onChange={handleCreateChange('verificationStatus')}>
                    <option value="unverified">Unverified</option>
                    <option value="pending_review">Pending Review</option>
                    <option value="verified">Verified</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-owner">Owner team</label>
                  <select
                    id="ci-owner"
                    value={formState.ownerTeamId}
                    onChange={handleCreateChange('ownerTeamId')}
                    required
                  >
                    <option value="">Select owner</option>
                    {teams.map((team) => (
                      <option key={team.id} value={team.id}>
                        {team.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-location">Location</label>
                  <input
                    id="ci-location"
                    value={formState.location}
                    onChange={handleCreateChange('location')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-version">Version</label>
                  <input
                    id="ci-version"
                    value={formState.version}
                    onChange={handleCreateChange('version')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-manufacturer">Manufacturer</label>
                  <input
                    id="ci-manufacturer"
                    value={formState.manufacturer}
                    onChange={handleCreateChange('manufacturer')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-serial">Serial Number</label>
                  <input
                    id="ci-serial"
                    value={formState.serialNumber}
                    onChange={handleCreateChange('serialNumber')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-acquisition">Acquisition Date</label>
                  <input
                    id="ci-acquisition"
                    type="date"
                    value={formState.acquisitionDate}
                    onChange={handleCreateChange('acquisitionDate')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-warranty">Warranty Expiry</label>
                  <input
                    id="ci-warranty"
                    type="date"
                    value={formState.warrantyExpiry}
                    onChange={handleCreateChange('warrantyExpiry')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-disposal">Disposal Date</label>
                  <input
                    id="ci-disposal"
                    type="date"
                    value={formState.disposalDate}
                    onChange={handleCreateChange('disposalDate')}
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="ci-impact">Impact analysis</label>
                  <textarea
                    id="ci-impact"
                    rows={3}
                    value={formState.impactAnalysis}
                    onChange={handleCreateChange('impactAnalysis')}
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="ci-relationship-target">Relationship target</label>
                  <select
                    id="ci-relationship-target"
                    value={formState.relationshipTargetId}
                    onChange={handleCreateChange('relationshipTargetId')}
                    required={relationshipRequired}
                    disabled={!relationshipRequired}
                  >
                    <option value="">Select target CI</option>
                    {relationshipTargets.map((ci) => (
                      <option key={ci.id} value={ci.id}>
                        {ci.ci_number} - {ci.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ci-relationship-type">Relationship type</label>
                  <select
                    id="ci-relationship-type"
                    value={formState.relationshipType}
                    onChange={handleCreateChange('relationshipType')}
                    required={relationshipRequired}
                    disabled={!relationshipRequired}
                  >
                    <option value="">Select type</option>
                    {relationshipOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button type="button" className="ghost" onClick={closeCreate} disabled={createSubmitting}>Cancel</button>
                <button
                  type="submit"
                  disabled={createSubmitting || (relationshipRequired && (!formState.relationshipTargetId || !formState.relationshipType))}
                >
                  {createSubmitting ? 'Saving...' : 'Save CI'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
