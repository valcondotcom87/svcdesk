import { useEffect, useMemo, useState } from 'react'
import { apiRequest, getToken } from '../api/client'

const defaultState = {
  type: 'incident',
  title: '',
  description: '',
  category: '',
  affectedService: '',
  urgency: '2',
  impact: '2',
  serviceId: '',
  priority: '2',
  requesterId: '',
  assignedToId: '',
  dueDate: '',
  slaPolicyId: '',
  changeType: 'normal',
  changeImpact: '3',
  implementationOwnerId: '',
  implementationDate: '',
  backoutDate: '',
  estimatedDurationMinutes: '',
  affectedServices: '',
  riskAssessment: '',
  riskMitigation: '',
  implementationPlan: '',
  backoutPlan: '',
  successCriteria: '',
  testResults: '',
  cabMembers: [],
  assetCategoryId: '',
  isMajor: false,
  majorIncidentLevel: '',
  communicationCadenceMinutes: '60',
  olaTargetMinutes: '',
  ucTargetMinutes: '',
  assetType: 'hardware',
  assetStatus: 'in_use',
  lifecycleStage: 'in_use',
  criticality: 'medium',
  businessOwner: '',
  technicalOwner: '',
  location: '',
  relatedService: '',
  purchaseDate: '',
  cost: '',
  warrantyExpires: '',
  serialNumber: '',
  systemName: '',
  dataClassification: 'internal',
  confidentialityImpact: 'moderate',
  integrityImpact: 'moderate',
  availabilityImpact: 'moderate',
  fipsImpactLevel: 'moderate',
  riskLevel: 'medium',
  recoveryPriority: 'p3',
  businessValue: 'medium',
  authorizationBoundary: '',
  dependencies: '',
  complianceTags: '',
  csfFunction: 'identify',
  csfCategory: '',
  isoControl: '',
  nistControl: '',
}

const affectedServiceOptions = [
  'Email & Collaboration',
  'Network & Connectivity',
  'VPN Access',
  'Wi-Fi Access',
  'Identity & Access',
  'Endpoint Devices',
  'Business Applications',
  'ERP/CRM/Finance',
  'Database Services',
  'Storage & Backup',
  'Virtualization/Cloud',
  'Telephony & Unified Comms',
  'Security Services',
  'Facilities & Environment',
]

export default function CreateTicketModal({ open, type, onClose, currentUser }) {
  const [formState, setFormState] = useState(defaultState)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [hasAttemptedSubmit, setHasAttemptedSubmit] = useState(false)
  const [services, setServices] = useState([])
  const [servicesLoading, setServicesLoading] = useState(false)
  const [slaPolicies, setSlaPolicies] = useState([])
  const [slaPoliciesLoading, setSlaPoliciesLoading] = useState(false)
  const [users, setUsers] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)
  const [assetCategories, setAssetCategories] = useState([])
  const [assetCategoriesLoading, setAssetCategoriesLoading] = useState(false)
  const [moduleCategories, setModuleCategories] = useState([])
  const [moduleCategoriesLoading, setModuleCategoriesLoading] = useState(false)

  const effectiveType = formState.type
  const isEndUser = currentUser?.role === 'end_user'
  const allowedTypes = isEndUser
    ? ['incident', 'service_request', 'problem']
    : ['incident', 'service_request', 'problem', 'change', 'asset']

  useEffect(() => {
    if (!open) {
      return
    }
    setFormState((prev) => ({
      ...defaultState,
      type: allowedTypes.includes(type || prev.type) ? (type || prev.type) : 'incident',
      requesterId: currentUser?.id ? String(currentUser.id) : '',
    }))
    setError('')
    setHasAttemptedSubmit(false)
  }, [open, type, currentUser])

  useEffect(() => {
    if (!open || effectiveType !== 'service_request') {
      return
    }
    setServicesLoading(true)
    setServices([])
    apiRequest('/service-requests/services/?ordering=name')
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setServices(list)
      })
      .catch(() => {
        setServices([])
      })
      .finally(() => {
        setServicesLoading(false)
      })
  }, [open, effectiveType])

  useEffect(() => {
    if (!open || effectiveType !== 'service_request') {
      return
    }
    setSlaPoliciesLoading(true)
    setSlaPolicies([])
    apiRequest('/sla/slas/?ordering=name')
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setSlaPolicies(list)
      })
      .catch(() => {
        setSlaPolicies([])
      })
      .finally(() => {
        setSlaPoliciesLoading(false)
      })
  }, [open, effectiveType])

  useEffect(() => {
    if (!open || !['service_request', 'change'].includes(effectiveType)) {
      return
    }
    setUsersLoading(true)
    setUsers([])
    apiRequest('/users/users/?is_active=true&ordering=first_name')
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setUsers(list)
      })
      .catch(() => {
        setUsers([])
      })
      .finally(() => {
        setUsersLoading(false)
      })
  }, [open, effectiveType])

  useEffect(() => {
    if (!open || effectiveType !== 'asset') {
      return
    }
    setAssetCategoriesLoading(true)
    setAssetCategories([])
    apiRequest('/assets/asset-categories/?ordering=name')
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setAssetCategories(list)
      })
      .catch(() => {
        setAssetCategories([])
      })
      .finally(() => {
        setAssetCategoriesLoading(false)
      })
  }, [open, effectiveType])

  useEffect(() => {
    const moduleMap = {
      incident: 'incidents',
      problem: 'problems',
      change: 'changes',
    }
    const moduleKey = moduleMap[effectiveType]
    if (!open || !moduleKey) {
      return
    }
    setModuleCategoriesLoading(true)
    setModuleCategories([])
    apiRequest(`/organizations/module-categories/?module=${moduleKey}&is_active=true&ordering=sort_order`)
      .then((payload) => {
        const list = Array.isArray(payload?.results) ? payload.results : Array.isArray(payload) ? payload : []
        setModuleCategories(list)
      })
      .catch(() => {
        setModuleCategories([])
      })
      .finally(() => {
        setModuleCategoriesLoading(false)
      })
  }, [open, effectiveType])

  const canSubmit = useMemo(() => {
    if (effectiveType === 'incident') {
      const baseRequired = Boolean(
        formState.title.trim() &&
        formState.description.trim() &&
        formState.category.trim()
      )
      if (!formState.isMajor) {
        return baseRequired
      }
      return Boolean(
        baseRequired &&
        formState.majorIncidentLevel &&
        Number(formState.communicationCadenceMinutes) > 0
      )
    }
    if (effectiveType === 'change') {
      return Boolean(
        formState.title.trim() &&
        formState.description.trim() &&
        formState.category.trim() &&
        formState.changeType &&
        formState.changeImpact &&
        formState.implementationDate &&
        formState.backoutDate &&
        formState.affectedServices.trim() &&
        formState.riskAssessment.trim() &&
        formState.riskMitigation.trim() &&
        formState.implementationPlan.trim() &&
        formState.backoutPlan.trim() &&
        formState.successCriteria.trim() &&
        formState.cabMembers.length > 0
      )
    }
    return Boolean(formState.title.trim() && formState.description.trim())
  }, [
    effectiveType,
    formState.title,
    formState.description,
    formState.category,
    formState.isMajor,
    formState.majorIncidentLevel,
    formState.communicationCadenceMinutes,
    formState.changeType,
    formState.changeImpact,
    formState.implementationDate,
    formState.backoutDate,
    formState.affectedServices,
    formState.riskAssessment,
    formState.riskMitigation,
    formState.implementationPlan,
    formState.backoutPlan,
    formState.successCriteria,
    formState.cabMembers,
  ])

  if (!open) {
    return null
  }

  const handleChange = (field) => (event) => {
    setFormState((prev) => ({
      ...prev,
      [field]: event.target.value,
    }))
  }

  const handleMultiSelectChange = (field) => (event) => {
    const values = Array.from(event.target.selectedOptions).map((option) => option.value)
    setFormState((prev) => ({
      ...prev,
      [field]: values,
    }))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()
    setHasAttemptedSubmit(true)
    if (isSubmitting) {
      return
    }

    if (!currentUser && !getToken()) {
      setError('Please sign in before creating a ticket.')
      return
    }

    if (!formState.title.trim() || !formState.description.trim()) {
      setError('Please complete the required fields before submitting.')
      return
    }

    setIsSubmitting(true)
    setError('')

    try {
      let created = null
      if (effectiveType === 'incident') {
        created = await apiRequest('/incidents/incidents/', {
          method: 'POST',
          body: {
            title: formState.title.trim(),
            description: formState.description.trim(),
            category: formState.category.trim(),
            affected_service: formState.affectedService.trim() || null,
            urgency: Number(formState.urgency),
            impact: Number(formState.impact),
            is_major: isEndUser ? false : formState.isMajor,
            major_incident_level: isEndUser || !formState.isMajor ? null : formState.majorIncidentLevel,
            communication_cadence_minutes: isEndUser || !formState.isMajor
              ? null
              : Number(formState.communicationCadenceMinutes),
            ola_target_minutes: formState.olaTargetMinutes ? Number(formState.olaTargetMinutes) : null,
            uc_target_minutes: formState.ucTargetMinutes ? Number(formState.ucTargetMinutes) : null,
            requester: currentUser?.id || null,
          },
        })
      } else if (effectiveType === 'service_request') {
        const dueDateValue = formState.dueDate ? new Date(formState.dueDate) : null
        created = await apiRequest('/service-requests/service-requests/', {
          method: 'POST',
          body: {
            title: formState.title.trim(),
            description: formState.description.trim(),
            service: formState.serviceId || null,
            priority: Number(formState.priority),
            requester: currentUser?.id || null,
            assigned_to: isEndUser ? null : (formState.assignedToId ? Number(formState.assignedToId) : null),
            due_date: isEndUser || !dueDateValue ? null : dueDateValue.toISOString(),
            sla_policy: isEndUser ? null : (formState.slaPolicyId ? Number(formState.slaPolicyId) : null),
          },
        })
      } else if (effectiveType === 'problem') {
        created = await apiRequest('/problems/problems/', {
          method: 'POST',
          body: {
            title: formState.title.trim(),
            description: formState.description.trim(),
            category: formState.category.trim(),
            owner: currentUser?.id || null,
          },
        })
      } else if (effectiveType === 'change') {
        created = await apiRequest('/changes/changes/', {
          method: 'POST',
          body: {
            title: formState.title.trim(),
            description: formState.description.trim(),
            category: formState.category.trim(),
            change_type: formState.changeType,
            impact_level: Number(formState.changeImpact),
            requester: currentUser?.id || null,
            implementation_owner: formState.implementationOwnerId ? Number(formState.implementationOwnerId) : null,
            implementation_date: formState.implementationDate ? new Date(formState.implementationDate).toISOString() : null,
            backout_date: formState.backoutDate ? new Date(formState.backoutDate).toISOString() : null,
            estimated_duration_minutes: formState.estimatedDurationMinutes
              ? Number(formState.estimatedDurationMinutes)
              : null,
            affected_services: formState.affectedServices.trim(),
            risk_assessment: formState.riskAssessment.trim(),
            risk_mitigation: formState.riskMitigation.trim(),
            implementation_plan: formState.implementationPlan.trim(),
            backout_plan: formState.backoutPlan.trim(),
            success_criteria: formState.successCriteria.trim(),
            test_results: formState.testResults.trim(),
            cab_members: formState.cabMembers,
          },
        })
      } else if (effectiveType === 'asset') {
        created = await apiRequest('/assets/assets/', {
          method: 'POST',
          body: {
            name: formState.title.trim(),
            description: formState.description.trim(),
            asset_type: formState.assetType,
            category: formState.assetCategoryId || null,
            status: formState.assetStatus,
            lifecycle_stage: formState.lifecycleStage,
            criticality: formState.criticality,
            current_owner: currentUser?.id || null,
            business_owner: formState.businessOwner.trim(),
            technical_owner: formState.technicalOwner.trim(),
            location: formState.location.trim(),
            related_service: formState.relatedService.trim(),
            purchase_date: formState.purchaseDate || null,
            cost: formState.cost ? Number(formState.cost) : null,
            warranty_expires: formState.warrantyExpires || null,
            serial_number: formState.serialNumber.trim(),
            system_name: formState.systemName.trim(),
            data_classification: formState.dataClassification,
            confidentiality_impact: formState.confidentialityImpact,
            integrity_impact: formState.integrityImpact,
            availability_impact: formState.availabilityImpact,
            fips_impact_level: formState.fipsImpactLevel,
            risk_level: formState.riskLevel,
            recovery_priority: formState.recoveryPriority,
            business_value: formState.businessValue,
            authorization_boundary: formState.authorizationBoundary.trim(),
            dependencies: formState.dependencies.trim(),
            compliance_tags: formState.complianceTags.trim(),
            csf_function: formState.csfFunction,
            csf_category: formState.csfCategory.trim(),
            iso_control: formState.isoControl.trim(),
            nist_control: formState.nistControl.trim(),
          },
        })
      }

      window.dispatchEvent(
        new CustomEvent('itsm:ticket-created', {
          detail: {
            type: effectiveType,
            id: created?.id || null,
            ticketNumber: created?.ticket_number || created?.ticket || null,
          },
        })
      )
      onClose()
    } catch (err) {
      const message = err?.payload?.detail || err?.payload?.error || err?.message || 'Unable to create ticket.'
      setError(message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" role="presentation">
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Create ticket"
        style={{ maxHeight: '90vh', overflow: 'hidden' }}
      >
        <div className="modal-header">
          <div>
            <h2>Create Record</h2>
            <p className="muted">Capture a new ITSM record.</p>
          </div>
          <button type="button" className="ghost" onClick={onClose}>Close</button>
        </div>

        <form
          className="modal-body"
          onSubmit={handleSubmit}
          style={{ overflowY: 'auto', paddingRight: '0.5rem' }}
        >
          {!currentUser && !getToken() && (
            <div className="banner">
              <div>
                <strong>Sign in required</strong>
                <div className="muted">Please sign in before creating a ticket.</div>
              </div>
            </div>
          )}

          <div className="form-grid">
            {isEndUser ? (
              <div className="banner" style={{ gridColumn: '1 / -1' }}>
                <strong>Quick form for end users</strong>
                <div className="muted">Fill the required fields and we will route it to the service desk.</div>
              </div>
            ) : null}
            <div className="form-field">
              <label htmlFor="ticket-type">Ticket type</label>
              <select id="ticket-type" value={formState.type} onChange={handleChange('type')}>
                {allowedTypes.includes('incident') && <option value="incident">Incident</option>}
                {allowedTypes.includes('service_request') && <option value="service_request">Service Request</option>}
                {allowedTypes.includes('problem') && <option value="problem">Problem</option>}
                {allowedTypes.includes('change') && <option value="change">Change</option>}
                {allowedTypes.includes('asset') && <option value="asset">Asset</option>}
              </select>
            </div>

            <div className="form-field">
              <label htmlFor="ticket-title">
                {effectiveType === 'asset' ? 'Asset name' : 'Title'}
              </label>
              <input
                id="ticket-title"
                value={formState.title}
                onChange={handleChange('title')}
                placeholder="Short summary of the issue"
                aria-invalid={hasAttemptedSubmit && !formState.title.trim()}
                required
              />
              {hasAttemptedSubmit && !formState.title.trim() ? (
                <div className="muted" style={{ color: '#b42318' }}>Title is required.</div>
              ) : null}
            </div>

            <div className="form-field form-field-full">
              <label htmlFor="ticket-description">Description</label>
              <textarea
                id="ticket-description"
                value={formState.description}
                onChange={handleChange('description')}
                placeholder="Describe what happened, impact, and any context"
                rows={4}
                aria-invalid={hasAttemptedSubmit && !formState.description.trim()}
                required
              />
              {hasAttemptedSubmit && !formState.description.trim() ? (
                <div className="muted" style={{ color: '#b42318' }}>Description is required.</div>
              ) : null}
            </div>

            {effectiveType === 'incident' ? (
              <>
                <div className="form-field">
                  <label htmlFor="ticket-category">Category</label>
                  <select
                    id="ticket-category"
                    value={formState.category}
                    onChange={handleChange('category')}
                    aria-invalid={hasAttemptedSubmit && !formState.category.trim()}
                    required
                  >
                    <option value="">Select a category</option>
                    {moduleCategories.map((category) => (
                      <option key={category.id} value={category.name}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  {moduleCategoriesLoading ? <span className="muted">Loading categories...</span> : null}
                  {hasAttemptedSubmit && !formState.category.trim() ? (
                    <div className="muted" style={{ color: '#b42318' }}>Category is required.</div>
                  ) : null}
                </div>
                <div className="form-field">
                  <label htmlFor="ticket-affected-service">Affected service (optional)</label>
                  <select
                    id="ticket-affected-service"
                    value={formState.affectedService}
                    onChange={handleChange('affectedService')}
                  >
                    <option value="">Select affected service</option>
                    {affectedServiceOptions.map((service) => (
                      <option key={service} value={service}>
                        {service}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ticket-urgency">Urgency</label>
                  <select id="ticket-urgency" value={formState.urgency} onChange={handleChange('urgency')}>
                    <option value="1">High</option>
                    <option value="2">Medium</option>
                    <option value="3">Low</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="ticket-impact">Impact</label>
                  <select id="ticket-impact" value={formState.impact} onChange={handleChange('impact')}>
                    <option value="1">High (Multiple users)</option>
                    <option value="2">Medium (Department)</option>
                    <option value="3">Low (Single user)</option>
                  </select>
                </div>
                {!isEndUser ? (
                  <>
                    <div className="form-field">
                      <label htmlFor="ticket-major">Major incident</label>
                      <select
                        id="ticket-major"
                        value={formState.isMajor ? 'yes' : 'no'}
                        onChange={(event) => setFormState((prev) => ({
                          ...prev,
                          isMajor: event.target.value === 'yes',
                          majorIncidentLevel: event.target.value === 'yes' ? prev.majorIncidentLevel : '',
                        }))}
                      >
                        <option value="no">No</option>
                        <option value="yes">Yes</option>
                      </select>
                    </div>
                    {formState.isMajor ? (
                      <>
                        <div className="form-field">
                          <label htmlFor="ticket-major-level">Major level</label>
                          <select
                            id="ticket-major-level"
                            value={formState.majorIncidentLevel}
                            onChange={handleChange('majorIncidentLevel')}
                            required
                          >
                            <option value="">Select level</option>
                            <option value="mi1">Major 1 (Critical)</option>
                            <option value="mi2">Major 2 (High)</option>
                            <option value="mi3">Major 3 (Medium)</option>
                          </select>
                        </div>
                        <div className="form-field">
                          <label htmlFor="ticket-comm-cadence">Communication cadence (minutes)</label>
                          <input
                            id="ticket-comm-cadence"
                            type="number"
                            min="15"
                            value={formState.communicationCadenceMinutes}
                            onChange={handleChange('communicationCadenceMinutes')}
                            required
                          />
                        </div>
                      </>
                    ) : null}
                  </>
                ) : null}
                {!isEndUser ? (
                  <>
                    <div className="form-field">
                      <label htmlFor="ticket-ola">OLA target (minutes)</label>
                      <input
                        id="ticket-ola"
                        type="number"
                        min="0"
                        value={formState.olaTargetMinutes}
                        onChange={handleChange('olaTargetMinutes')}
                        placeholder="Optional"
                      />
                    </div>
                    <div className="form-field">
                      <label htmlFor="ticket-uc">UC target (minutes)</label>
                      <input
                        id="ticket-uc"
                        type="number"
                        min="0"
                        value={formState.ucTargetMinutes}
                        onChange={handleChange('ucTargetMinutes')}
                        placeholder="Optional"
                      />
                    </div>
                  </>
                ) : null}
              </>
            ) : effectiveType === 'service_request' ? (
              <>
                <div className="form-field">
                  <label htmlFor="ticket-service">Service (optional)</label>
                  <select
                    id="ticket-service"
                    value={formState.serviceId}
                    onChange={handleChange('serviceId')}
                    disabled={servicesLoading}
                  >
                    <option value="">Select a service</option>
                    {services.map((service) => (
                      <option key={service.id} value={service.id}>
                        {service.name}
                      </option>
                    ))}
                  </select>
                </div>
                {!isEndUser ? (
                  <div className="form-field">
                    <label htmlFor="ticket-requester">Requested for</label>
                    <select
                      id="ticket-requester"
                      value={formState.requesterId}
                      onChange={handleChange('requesterId')}
                      disabled={usersLoading}
                    >
                      <option value="">Use current user</option>
                      {users.map((user) => (
                        <option key={user.id} value={user.id}>
                          {user.full_name || user.email || user.username}
                        </option>
                      ))}
                    </select>
                  </div>
                ) : null}
                <div className="form-field">
                  <label htmlFor="ticket-priority">Priority</label>
                  <select id="ticket-priority" value={formState.priority} onChange={handleChange('priority')}>
                    <option value="1">High</option>
                    <option value="2">Medium</option>
                    <option value="3">Low</option>
                  </select>
                </div>
                {!isEndUser ? (
                  <>
                    <div className="form-field">
                      <label htmlFor="ticket-assigned-to">Assigned to (optional)</label>
                      <select
                        id="ticket-assigned-to"
                        value={formState.assignedToId}
                        onChange={handleChange('assignedToId')}
                        disabled={usersLoading}
                      >
                        <option value="">Unassigned</option>
                        {users.map((user) => (
                          <option key={user.id} value={user.id}>
                            {user.full_name || user.email || user.username}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="form-field">
                      <label htmlFor="ticket-due-date">Target due date (optional)</label>
                      <input
                        id="ticket-due-date"
                        type="datetime-local"
                        value={formState.dueDate}
                        onChange={handleChange('dueDate')}
                      />
                    </div>
                    <div className="form-field">
                      <label htmlFor="ticket-sla-policy">SLA policy (optional)</label>
                      <select
                        id="ticket-sla-policy"
                        value={formState.slaPolicyId}
                        onChange={handleChange('slaPolicyId')}
                        disabled={slaPoliciesLoading}
                      >
                        <option value="">Default policy</option>
                        {slaPolicies.map((policy) => (
                          <option key={policy.id} value={policy.id}>
                            {policy.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </>
                ) : (
                  <div className="form-field form-field-full">
                    <div className="muted">We will route and prioritize this request automatically.</div>
                  </div>
                )}
              </>
            ) : effectiveType === 'change' ? (
              <>
                <div className="form-field">
                  <label htmlFor="change-category">Category</label>
                  <select
                    id="change-category"
                    value={formState.category}
                    onChange={handleChange('category')}
                    required
                  >
                    <option value="">Select a category</option>
                    {moduleCategories.map((category) => (
                      <option key={category.id} value={category.name}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                  {moduleCategoriesLoading ? <span className="muted">Loading categories...</span> : null}
                </div>
                <div className="form-field">
                  <label htmlFor="change-type">Change type</label>
                  <select id="change-type" value={formState.changeType} onChange={handleChange('changeType')}>
                    <option value="standard">Standard</option>
                    <option value="normal">Normal</option>
                    <option value="emergency">Emergency</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="change-impact">Impact level</label>
                  <select id="change-impact" value={formState.changeImpact} onChange={handleChange('changeImpact')}>
                    <option value="1">Critical</option>
                    <option value="2">High</option>
                    <option value="3">Medium</option>
                    <option value="4">Low</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="change-owner">Implementation owner</label>
                  <select
                    id="change-owner"
                    value={formState.implementationOwnerId}
                    onChange={handleChange('implementationOwnerId')}
                    disabled={usersLoading}
                  >
                    <option value="">Select owner</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.full_name || user.email || user.username}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="change-implementation-date">Planned start</label>
                  <input
                    id="change-implementation-date"
                    type="datetime-local"
                    value={formState.implementationDate}
                    onChange={handleChange('implementationDate')}
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="change-backout-date">Planned end</label>
                  <input
                    id="change-backout-date"
                    type="datetime-local"
                    value={formState.backoutDate}
                    onChange={handleChange('backoutDate')}
                    required
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="change-duration">Estimated duration (minutes)</label>
                  <input
                    id="change-duration"
                    type="number"
                    min="0"
                    value={formState.estimatedDurationMinutes}
                    onChange={handleChange('estimatedDurationMinutes')}
                    placeholder="Optional"
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-affected-services">Affected CI/service</label>
                  <input
                    id="change-affected-services"
                    value={formState.affectedServices}
                    onChange={handleChange('affectedServices')}
                    placeholder="ERP, Email, Network"
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-risk">Risk assessment</label>
                  <textarea
                    id="change-risk"
                    rows={3}
                    value={formState.riskAssessment}
                    onChange={handleChange('riskAssessment')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-mitigation">Risk mitigation</label>
                  <textarea
                    id="change-mitigation"
                    rows={3}
                    value={formState.riskMitigation}
                    onChange={handleChange('riskMitigation')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-implementation-plan">Implementation plan</label>
                  <textarea
                    id="change-implementation-plan"
                    rows={3}
                    value={formState.implementationPlan}
                    onChange={handleChange('implementationPlan')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-backout-plan">Backout plan</label>
                  <textarea
                    id="change-backout-plan"
                    rows={3}
                    value={formState.backoutPlan}
                    onChange={handleChange('backoutPlan')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-success">Test/validation plan</label>
                  <textarea
                    id="change-success"
                    rows={3}
                    value={formState.successCriteria}
                    onChange={handleChange('successCriteria')}
                    required
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-test-results">Test results (optional)</label>
                  <textarea
                    id="change-test-results"
                    rows={2}
                    value={formState.testResults}
                    onChange={handleChange('testResults')}
                    placeholder="Optional"
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="change-cab">CAB members</label>
                  <select
                    id="change-cab"
                    multiple
                    value={formState.cabMembers}
                    onChange={handleMultiSelectChange('cabMembers')}
                    disabled={usersLoading}
                    required
                  >
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.full_name || user.email || user.username}
                      </option>
                    ))}
                  </select>
                  <span className="muted">Use Ctrl/Cmd to select multiple members.</span>
                </div>
              </>
            ) : effectiveType === 'problem' ? (
              <>
                <div className="form-field">
                  <label htmlFor="problem-category">Category (optional)</label>
                  <input
                    id="problem-category"
                    list="problem-categories"
                    value={formState.category}
                    onChange={handleChange('category')}
                    placeholder="Network, Database, Application"
                  />
                  <datalist id="problem-categories">
                    {moduleCategories.map((category) => (
                      <option key={category.id} value={category.name} />
                    ))}
                  </datalist>
                  {moduleCategoriesLoading ? <span className="muted">Loading categories...</span> : null}
                </div>
              </>
            ) : effectiveType === 'asset' ? (
              <>
                <div className="form-field">
                  <label htmlFor="asset-category">Asset category (optional)</label>
                  <select
                    id="asset-category"
                    value={formState.assetCategoryId}
                    onChange={handleChange('assetCategoryId')}
                    disabled={assetCategoriesLoading}
                  >
                    <option value="">Select a category</option>
                    {assetCategories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-type">Asset type</label>
                  <select id="asset-type" value={formState.assetType} onChange={handleChange('assetType')}>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="virtual">Virtual</option>
                    <option value="network">Network</option>
                    <option value="data">Data</option>
                    <option value="service">Service</option>
                    <option value="facility">Facility</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-status">Status</label>
                  <select id="asset-status" value={formState.assetStatus} onChange={handleChange('assetStatus')}>
                    <option value="in_use">In Use</option>
                    <option value="in_stock">In Stock</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="planned">Planned</option>
                    <option value="retired">Retired</option>
                    <option value="disposed">Disposed</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-lifecycle">Lifecycle stage</label>
                  <select id="asset-lifecycle" value={formState.lifecycleStage} onChange={handleChange('lifecycleStage')}>
                    <option value="planning">Planning</option>
                    <option value="acquisition">Acquisition</option>
                    <option value="in_use">In Use</option>
                    <option value="maintenance">Maintenance</option>
                    <option value="retired">Retired</option>
                    <option value="disposed">Disposed</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-criticality">Criticality</label>
                  <select id="asset-criticality" value={formState.criticality} onChange={handleChange('criticality')}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-business-owner">Business owner</label>
                  <input
                    id="asset-business-owner"
                    value={formState.businessOwner}
                    onChange={handleChange('businessOwner')}
                    placeholder="Business owner name"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-technical-owner">Technical owner</label>
                  <input
                    id="asset-technical-owner"
                    value={formState.technicalOwner}
                    onChange={handleChange('technicalOwner')}
                    placeholder="Technical owner name"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-location">Location (optional)</label>
                  <input
                    id="asset-location"
                    value={formState.location}
                    onChange={handleChange('location')}
                    placeholder="HQ - Floor 3"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-related-service">Related service (optional)</label>
                  <input
                    id="asset-related-service"
                    value={formState.relatedService}
                    onChange={handleChange('relatedService')}
                    placeholder="Email Service, ERP"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-purchase-date">Purchase date (optional)</label>
                  <input
                    id="asset-purchase-date"
                    type="date"
                    value={formState.purchaseDate}
                    onChange={handleChange('purchaseDate')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-cost">Cost (optional)</label>
                  <input
                    id="asset-cost"
                    type="number"
                    min="0"
                    step="0.01"
                    value={formState.cost}
                    onChange={handleChange('cost')}
                    placeholder="0.00"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-warranty">Warranty expires (optional)</label>
                  <input
                    id="asset-warranty"
                    type="date"
                    value={formState.warrantyExpires}
                    onChange={handleChange('warrantyExpires')}
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-serial">Serial number (optional)</label>
                  <input
                    id="asset-serial"
                    value={formState.serialNumber}
                    onChange={handleChange('serialNumber')}
                    placeholder="Serial number"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-system">System name (optional)</label>
                  <input
                    id="asset-system"
                    value={formState.systemName}
                    onChange={handleChange('systemName')}
                    placeholder="System/application name"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-data-class">Data classification</label>
                  <select id="asset-data-class" value={formState.dataClassification} onChange={handleChange('dataClassification')}>
                    <option value="public">Public</option>
                    <option value="internal">Internal</option>
                    <option value="confidential">Confidential</option>
                    <option value="restricted">Restricted</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-confidentiality">Confidentiality impact</label>
                  <select
                    id="asset-confidentiality"
                    value={formState.confidentialityImpact}
                    onChange={handleChange('confidentialityImpact')}
                  >
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-integrity">Integrity impact</label>
                  <select
                    id="asset-integrity"
                    value={formState.integrityImpact}
                    onChange={handleChange('integrityImpact')}
                  >
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-availability">Availability impact</label>
                  <select
                    id="asset-availability"
                    value={formState.availabilityImpact}
                    onChange={handleChange('availabilityImpact')}
                  >
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-fips">FIPS impact level</label>
                  <select id="asset-fips" value={formState.fipsImpactLevel} onChange={handleChange('fipsImpactLevel')}>
                    <option value="low">Low</option>
                    <option value="moderate">Moderate</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-risk">Risk level</label>
                  <select id="asset-risk" value={formState.riskLevel} onChange={handleChange('riskLevel')}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-recovery">Recovery priority</label>
                  <select id="asset-recovery" value={formState.recoveryPriority} onChange={handleChange('recoveryPriority')}>
                    <option value="p1">P1 - Critical</option>
                    <option value="p2">P2 - High</option>
                    <option value="p3">P3 - Medium</option>
                    <option value="p4">P4 - Low</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-business-value">Business value</label>
                  <select id="asset-business-value" value={formState.businessValue} onChange={handleChange('businessValue')}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="asset-authorization">Authorization boundary (optional)</label>
                  <textarea
                    id="asset-authorization"
                    value={formState.authorizationBoundary}
                    onChange={handleChange('authorizationBoundary')}
                    rows={2}
                    placeholder="Scope of authorization boundary"
                  />
                </div>
                <div className="form-field form-field-full">
                  <label htmlFor="asset-dependencies">Dependencies (optional)</label>
                  <textarea
                    id="asset-dependencies"
                    value={formState.dependencies}
                    onChange={handleChange('dependencies')}
                    rows={2}
                    placeholder="Upstream/downstream dependencies"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-compliance">Compliance tags (optional)</label>
                  <input
                    id="asset-compliance"
                    value={formState.complianceTags}
                    onChange={handleChange('complianceTags')}
                    placeholder="ITIL, NIST 800-53, NIST CSF, ISO 27001"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-csf">NIST CSF Function</label>
                  <select id="asset-csf" value={formState.csfFunction} onChange={handleChange('csfFunction')}>
                    <option value="govern">Govern</option>
                    <option value="identify">Identify</option>
                    <option value="protect">Protect</option>
                    <option value="detect">Detect</option>
                    <option value="respond">Respond</option>
                    <option value="recover">Recover</option>
                  </select>
                </div>
                <div className="form-field">
                  <label htmlFor="asset-csf-category">NIST CSF Category (optional)</label>
                  <input
                    id="asset-csf-category"
                    value={formState.csfCategory}
                    onChange={handleChange('csfCategory')}
                    placeholder="ID.AM, PR.AC, DE.CM"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-iso-control">ISO 27001 Control (optional)</label>
                  <input
                    id="asset-iso-control"
                    value={formState.isoControl}
                    onChange={handleChange('isoControl')}
                    placeholder="A.5.1, A.8.1"
                  />
                </div>
                <div className="form-field">
                  <label htmlFor="asset-nist-control">NIST Control (optional)</label>
                  <input
                    id="asset-nist-control"
                    value={formState.nistControl}
                    onChange={handleChange('nistControl')}
                    placeholder="AC-1, SI-2"
                  />
                </div>
              </>
            ) : null}
          </div>

          {error ? <div className="form-error">{error}</div> : null}
          {!error && hasAttemptedSubmit && !canSubmit ? (
            <div className="form-error">Title and description are required.</div>
          ) : null}

          <div className="modal-actions">
            <button type="button" className="ghost" onClick={onClose}>Cancel</button>
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Creating...' : 'Create Ticket'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
