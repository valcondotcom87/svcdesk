import { useEffect, useMemo, useState } from 'react'
import PageHeader from '../components/PageHeader.jsx'
import { useApi } from '../api/hooks.js'
import {
  apiRequest,
  setToken,
  setRefreshToken,
  setStoredUser,
  clearAuth,
} from '../api/client'

const ROLE_OPTIONS = [
  { value: 'end_user', label: 'End User' },
  { value: 'asset_manager', label: 'Asset Manager' },
  { value: 'engineer', label: 'Engineer' },
  { value: 'agent', label: 'Agent' },
  { value: 'manager', label: 'Manager' },
  { value: 'admin', label: 'Administrator' },
]

const MODULE_OPTIONS = [
  { value: 'incidents', label: 'Incidents' },
  { value: 'service_requests', label: 'Service Requests' },
  { value: 'problems', label: 'Problems' },
  { value: 'changes', label: 'Changes' },
  { value: 'assets', label: 'Assets' },
]

const IMPERSONATOR_ACCESS_KEY = 'itsm_impersonator_access'
const IMPERSONATOR_REFRESH_KEY = 'itsm_impersonator_refresh'
const IMPERSONATOR_USER_KEY = 'itsm_impersonator_user'

export default function Admin() {
  const { data: usersData, reload: reloadUsers } = useApi('/users/?page_size=100')
  const { data: orgData, reload: reloadOrgs } = useApi('/user-organizations/?page_size=100')
  const { data: rolesData } = useApi('/roles/?page_size=200')
  const { data: adSyncLogData, reload: reloadAdSyncLogs } = useApi('/ad-sync-logs/?ordering=-started_at&page_size=25')
  const { data: adConfigData, reload: reloadAdConfig } = useApi('/ad-configuration/?page_size=1')
  const [selectedModule, setSelectedModule] = useState('incidents')
  const { data: categoryData, reload: reloadCategories } = useApi(
    `/organizations/module-categories/?module=${selectedModule}&page_size=200`
  )

  const users = Array.isArray(usersData?.results) ? usersData.results : Array.isArray(usersData) ? usersData : []
  const organizations = Array.isArray(orgData?.results) ? orgData.results : Array.isArray(orgData) ? orgData : []
  const roles = Array.isArray(rolesData?.results) ? rolesData.results : Array.isArray(rolesData) ? rolesData : []
  const categories = Array.isArray(categoryData?.results) ? categoryData.results : Array.isArray(categoryData) ? categoryData : []
  const adSyncLogs = Array.isArray(adSyncLogData?.results) ? adSyncLogData.results : Array.isArray(adSyncLogData) ? adSyncLogData : []
  const adConfigs = Array.isArray(adConfigData?.results) ? adConfigData.results : Array.isArray(adConfigData) ? adConfigData : []
  const adConfig = adConfigs[0] || null

  const [userForm, setUserForm] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
    role: 'end_user',
    organization: '',
    mfa_enabled: false,
  })
  const [orgForm, setOrgForm] = useState({ name: '', domain: '' })
  const [selectedOrgId, setSelectedOrgId] = useState('')
  const [orgEditForm, setOrgEditForm] = useState({ name: '', domain: '', is_active: true })
  const [categoryForm, setCategoryForm] = useState({ name: '', description: '', sortOrder: 0 })
  const [message, setMessage] = useState('')
  const [adConfigMessage, setAdConfigMessage] = useState('')
  const [adConfigBusy, setAdConfigBusy] = useState(false)
  const [adConfigForm, setAdConfigForm] = useState({
    server_name: '',
    server_port: 389,
    use_ssl: false,
    bind_username: '',
    bind_password: '',
    search_base: '',
    search_filter: '(objectClass=user)',
    username_attribute: 'sAMAccountName',
    email_attribute: 'mail',
    first_name_attribute: 'givenName',
    last_name_attribute: 'sn',
    phone_attribute: 'telephoneNumber',
    group_base: '',
    group_member_attribute: 'member',
    auto_create_users: true,
    auto_update_users: true,
    auto_disable_missing_users: false,
    is_enabled: false,
  })
  const [selectedUserId, setSelectedUserId] = useState('')
  const [editForm, setEditForm] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    role: 'end_user',
    is_active: true,
    mfa_enabled: false,
  })
  const [assignRoleId, setAssignRoleId] = useState('')
  const { data: userRoleData, reload: reloadUserRoles } = useApi(
    selectedUserId ? `/user-roles/?user=${selectedUserId}` : null,
    { enabled: Boolean(selectedUserId) }
  )
  const userRoles = Array.isArray(userRoleData?.results) ? userRoleData.results : Array.isArray(userRoleData) ? userRoleData : []

  const handleFormChange = (setter) => (field) => (event) => {
    setter((prev) => ({ ...prev, [field]: event.target.value }))
  }

  const handleCheckboxChange = (setter) => (field) => (event) => {
    setter((prev) => ({ ...prev, [field]: event.target.checked }))
  }

  useEffect(() => {
    if (!adConfig) {
      return
    }
    setAdConfigForm({
      server_name: adConfig.server_name || '',
      server_port: adConfig.server_port || 389,
      use_ssl: Boolean(adConfig.use_ssl),
      bind_username: adConfig.bind_username || '',
      bind_password: '',
      search_base: adConfig.search_base || '',
      search_filter: adConfig.search_filter || '(objectClass=user)',
      username_attribute: adConfig.username_attribute || 'sAMAccountName',
      email_attribute: adConfig.email_attribute || 'mail',
      first_name_attribute: adConfig.first_name_attribute || 'givenName',
      last_name_attribute: adConfig.last_name_attribute || 'sn',
      phone_attribute: adConfig.phone_attribute || 'telephoneNumber',
      group_base: adConfig.group_base || '',
      group_member_attribute: adConfig.group_member_attribute || 'member',
      auto_create_users: Boolean(adConfig.auto_create_users),
      auto_update_users: Boolean(adConfig.auto_update_users),
      auto_disable_missing_users: Boolean(adConfig.auto_disable_missing_users),
      is_enabled: Boolean(adConfig.is_enabled),
    })
  }, [adConfig])

  const isImpersonating = useMemo(() => Boolean(localStorage.getItem(IMPERSONATOR_ACCESS_KEY)), [])

  const handleSelectUser = (user) => {
    setSelectedUserId(user.id)
    setEditForm({
      first_name: user.first_name || '',
      last_name: user.last_name || '',
      phone: user.phone || '',
      role: user.role || 'end_user',
      is_active: Boolean(user.is_active),
      mfa_enabled: Boolean(user.mfa_enabled),
    })
  }

  const handleCreateUser = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      await apiRequest('/users/', {
        method: 'POST',
        body: {
          username: userForm.username.trim(),
          email: userForm.email.trim(),
          password: userForm.password,
          password_confirm: userForm.passwordConfirm,
          role: userForm.role,
          organization: userForm.organization || null,
          mfa_enabled: userForm.mfa_enabled,
        },
      })
      setUserForm({
        username: '',
        email: '',
        password: '',
        passwordConfirm: '',
        role: 'end_user',
        organization: '',
        mfa_enabled: false,
      })
      reloadUsers()
      setMessage('User created.')
    } catch (error) {
      setMessage(error?.payload?.error?.message || error?.payload?.detail || error.message)
    }
  }

  const handleUpdateUser = async (event) => {
    event.preventDefault()
    if (!selectedUserId) {
      return
    }
    setMessage('')
    try {
      await apiRequest(`/users/${selectedUserId}/`, {
        method: 'PATCH',
        body: {
          first_name: editForm.first_name,
          last_name: editForm.last_name,
          phone: editForm.phone,
          role: editForm.role,
          is_active: editForm.is_active,
          mfa_enabled: editForm.mfa_enabled,
        },
      })
      reloadUsers()
      setMessage('User updated.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleDeactivateUser = async (userId) => {
    setMessage('')
    try {
      await apiRequest(`/users/${userId}/`, { method: 'DELETE' })
      reloadUsers()
      setMessage('User deactivated.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleAssignRole = async (event) => {
    event.preventDefault()
    if (!selectedUserId || !assignRoleId) {
      return
    }
    setMessage('')
    try {
      await apiRequest(`/roles/${assignRoleId}/assign_user/`, {
        method: 'POST',
        body: { user_id: selectedUserId },
      })
      setAssignRoleId('')
      reloadUserRoles()
      setMessage('Role assigned.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleUnassignRole = async (roleId) => {
    setMessage('')
    try {
      await apiRequest(`/roles/${roleId}/unassign_user/`, {
        method: 'DELETE',
        body: { user_id: selectedUserId },
      })
      reloadUserRoles()
      setMessage('Role unassigned.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleCreateOrg = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      await apiRequest('/user-organizations/', {
        method: 'POST',
        body: {
          name: orgForm.name.trim(),
          domain: orgForm.domain.trim() || null,
          is_active: true,
        },
      })
      setOrgForm({ name: '', domain: '' })
      reloadOrgs()
      setMessage('Organization created.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleSelectOrg = (org) => {
    setSelectedOrgId(org.id)
    setOrgEditForm({
      name: org.name || '',
      domain: org.domain || '',
      is_active: Boolean(org.is_active),
    })
  }

  const handleUpdateOrg = async (event) => {
    event.preventDefault()
    if (!selectedOrgId) {
      return
    }
    setMessage('')
    try {
      await apiRequest(`/user-organizations/${selectedOrgId}/`, {
        method: 'PATCH',
        body: {
          name: orgEditForm.name.trim(),
          domain: orgEditForm.domain.trim() || null,
          is_active: orgEditForm.is_active,
        },
      })
      reloadOrgs()
      setMessage('Organization updated.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleDeactivateOrg = async (orgId) => {
    setMessage('')
    try {
      await apiRequest(`/user-organizations/${orgId}/`, {
        method: 'PATCH',
        body: { is_active: false },
      })
      reloadOrgs()
      setMessage('Organization deactivated.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleAdConfigChange = (field) => (event) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : event.target.value
    setAdConfigForm((prev) => ({ ...prev, [field]: value }))
  }

  const handleSaveAdConfig = async (event) => {
    event.preventDefault()
    setAdConfigMessage('')
    if (!adConfigForm.bind_password) {
      setAdConfigMessage('Bind password is required for saving configuration.')
      return
    }
    setAdConfigBusy(true)
    try {
      const payload = {
        ...adConfigForm,
        server_port: Number(adConfigForm.server_port) || 389,
      }
      if (adConfig?.id) {
        await apiRequest(`/ad-configuration/${adConfig.id}/`, {
          method: 'PATCH',
          body: payload,
        })
        setAdConfigMessage('AD configuration updated.')
      } else {
        await apiRequest('/ad-configuration/', {
          method: 'POST',
          body: payload,
        })
        setAdConfigMessage('AD configuration created.')
      }
      reloadAdConfig()
    } catch (error) {
      setAdConfigMessage(error?.payload?.detail || error.message)
    } finally {
      setAdConfigBusy(false)
    }
  }

  const handleTestAdConnection = async () => {
    if (!adConfig?.id) {
      setAdConfigMessage('Save configuration before testing connection.')
      return
    }
    setAdConfigMessage('')
    setAdConfigBusy(true)
    try {
      const result = await apiRequest(`/ad-configuration/${adConfig.id}/test_connection/`, {
        method: 'POST',
      })
      setAdConfigMessage(result?.message || 'Connection test completed.')
    } catch (error) {
      setAdConfigMessage(error?.payload?.detail || error.message)
    } finally {
      setAdConfigBusy(false)
    }
  }

  const handleSyncAdNow = async () => {
    if (!adConfig?.id) {
      setAdConfigMessage('Save configuration before syncing.')
      return
    }
    setAdConfigMessage('')
    setAdConfigBusy(true)
    try {
      const result = await apiRequest(`/ad-configuration/${adConfig.id}/sync_now/`, {
        method: 'POST',
      })
      setAdConfigMessage(result?.message || 'Sync started.')
      reloadAdSyncLogs()
      reloadAdConfig()
    } catch (error) {
      setAdConfigMessage(error?.payload?.detail || error.message)
    } finally {
      setAdConfigBusy(false)
    }
  }

  const handleImpersonate = async (userId) => {
    setMessage('')
    try {
      if (!localStorage.getItem(IMPERSONATOR_ACCESS_KEY)) {
        localStorage.setItem(IMPERSONATOR_ACCESS_KEY, localStorage.getItem('itsm_access_token') || '')
        localStorage.setItem(IMPERSONATOR_REFRESH_KEY, localStorage.getItem('itsm_refresh_token') || '')
        localStorage.setItem(IMPERSONATOR_USER_KEY, localStorage.getItem('itsm_user') || '')
      }
      const result = await apiRequest(`/users/${userId}/impersonate/`, { method: 'POST' })
      setToken(result.access)
      setRefreshToken(result.refresh)
      if (result.user) {
        setStoredUser(result.user)
      }
      window.location.reload()
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleStopImpersonation = () => {
    const originalAccess = localStorage.getItem(IMPERSONATOR_ACCESS_KEY)
    const originalRefresh = localStorage.getItem(IMPERSONATOR_REFRESH_KEY)
    const originalUser = localStorage.getItem(IMPERSONATOR_USER_KEY)

    clearAuth()
    if (originalAccess) {
      setToken(originalAccess)
    }
    if (originalRefresh) {
      setRefreshToken(originalRefresh)
    }
    if (originalUser) {
      localStorage.setItem('itsm_user', originalUser)
    }
    localStorage.removeItem(IMPERSONATOR_ACCESS_KEY)
    localStorage.removeItem(IMPERSONATOR_REFRESH_KEY)
    localStorage.removeItem(IMPERSONATOR_USER_KEY)
    window.location.reload()
  }

  const handleCreateCategory = async (event) => {
    event.preventDefault()
    setMessage('')
    try {
      await apiRequest('/organizations/module-categories/', {
        method: 'POST',
        body: {
          module: selectedModule,
          name: categoryForm.name.trim(),
          description: categoryForm.description.trim(),
          sort_order: Number(categoryForm.sortOrder),
          is_active: true,
        },
      })
      setCategoryForm({ name: '', description: '', sortOrder: 0 })
      reloadCategories()
      setMessage('Category created.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  const handleDeleteCategory = async (categoryId) => {
    setMessage('')
    try {
      await apiRequest(`/organizations/module-categories/${categoryId}/`, { method: 'DELETE' })
      reloadCategories()
      setMessage('Category deleted.')
    } catch (error) {
      setMessage(error?.payload?.detail || error.message)
    }
  }

  return (
    <div className="fade-in">
      <PageHeader
        title="Administration"
        subtitle="User management, directory sync, impersonation, and categories"
        actions={isImpersonating ? (
          <button type="button" className="ghost" onClick={handleStopImpersonation}>Stop Impersonation</button>
        ) : null}
      />

      {message ? <div className="banner">{message}</div> : null}

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>User Management</h3>
        <div className="table" style={{ marginBottom: '1rem' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan="5" className="table-empty">No users found.</td>
                </tr>
              ) : users.map((user) => (
                <tr key={user.id}>
                  <td>{user.full_name || user.username}</td>
                  <td>{user.email}</td>
                  <td>{user.role}</td>
                  <td>{user.is_active ? 'Active' : 'Inactive'}</td>
                  <td>
                    <button type="button" className="ghost" onClick={() => handleSelectUser(user)}>Edit</button>
                    <button type="button" className="ghost" onClick={() => handleDeactivateUser(user.id)}>Deactivate</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selectedUserId ? (
          <div className="split-grid" style={{ marginBottom: '1rem' }}>
            <form className="form-grid" onSubmit={handleUpdateUser}>
              <div className="form-field">
                <label>First name</label>
                <input value={editForm.first_name} onChange={handleFormChange(setEditForm)('first_name')} />
              </div>
              <div className="form-field">
                <label>Last name</label>
                <input value={editForm.last_name} onChange={handleFormChange(setEditForm)('last_name')} />
              </div>
              <div className="form-field">
                <label>Phone</label>
                <input value={editForm.phone} onChange={handleFormChange(setEditForm)('phone')} />
              </div>
              <div className="form-field">
                <label>Role</label>
                <select value={editForm.role} onChange={handleFormChange(setEditForm)('role')}>
                  {ROLE_OPTIONS.map((role) => (
                    <option key={role.value} value={role.value}>{role.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-field">
                <label>Status</label>
                <select value={editForm.is_active ? 'true' : 'false'} onChange={(event) => setEditForm((prev) => ({ ...prev, is_active: event.target.value === 'true' }))}>
                  <option value="true">Active</option>
                  <option value="false">Inactive</option>
                </select>
              </div>
              <div className="form-field">
                <label>
                  <input type="checkbox" checked={editForm.mfa_enabled} onChange={handleCheckboxChange(setEditForm)('mfa_enabled')} /> Enable MFA
                </label>
              </div>
              <div className="form-field">
                <button type="submit">Save Changes</button>
              </div>
            </form>

            <div>
              <h4>Role Assignments</h4>
              <form className="form-grid" onSubmit={handleAssignRole}>
                <div className="form-field">
                  <label>Assign role</label>
                  <select value={assignRoleId} onChange={(event) => setAssignRoleId(event.target.value)}>
                    <option value="">Select role</option>
                    {roles.map((role) => (
                      <option key={role.id} value={role.id}>{role.name}</option>
                    ))}
                  </select>
                </div>
                <div className="form-field">
                  <button type="submit">Assign</button>
                </div>
              </form>

              <div className="table" style={{ marginTop: '1rem' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Role</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {userRoles.length === 0 ? (
                      <tr>
                        <td colSpan="2" className="table-empty">No roles assigned.</td>
                      </tr>
                    ) : userRoles.map((userRole) => (
                      <tr key={userRole.id}>
                        <td>{userRole.role_name}</td>
                        <td>
                          <button type="button" className="ghost" onClick={() => handleUnassignRole(userRole.role)}>
                            Unassign
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : null}

        <form className="form-grid" onSubmit={handleCreateUser}>
          <div className="form-field">
            <label>Username</label>
            <input value={userForm.username} onChange={handleFormChange(setUserForm)('username')} required />
          </div>
          <div className="form-field">
            <label>Email</label>
            <input value={userForm.email} onChange={handleFormChange(setUserForm)('email')} required />
          </div>
          <div className="form-field">
            <label>Password</label>
            <input type="password" value={userForm.password} onChange={handleFormChange(setUserForm)('password')} required />
          </div>
          <div className="form-field">
            <label>Confirm Password</label>
            <input type="password" value={userForm.passwordConfirm} onChange={handleFormChange(setUserForm)('passwordConfirm')} required />
          </div>
          <div className="form-field">
            <label>Role</label>
            <select value={userForm.role} onChange={handleFormChange(setUserForm)('role')}>
              {ROLE_OPTIONS.map((role) => (
                <option key={role.value} value={role.value}>{role.label}</option>
              ))}
            </select>
          </div>
          <div className="form-field">
            <label>Organization</label>
            <select value={userForm.organization} onChange={handleFormChange(setUserForm)('organization')}>
              <option value="">Select organization</option>
              {organizations.map((org) => (
                <option key={org.id} value={org.id}>{org.name}</option>
              ))}
            </select>
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={userForm.mfa_enabled} onChange={handleCheckboxChange(setUserForm)('mfa_enabled')} /> Enable MFA
            </label>
          </div>
          <div className="form-field form-field-full">
            <button type="submit">Create User</button>
          </div>
        </form>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>Organization Management</h3>
        <div className="table" style={{ marginBottom: '1rem' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Domain</th>
                <th>Active</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {organizations.length === 0 ? (
                <tr>
                  <td colSpan="4" className="table-empty">No organizations found.</td>
                </tr>
              ) : organizations.map((org) => (
                <tr key={org.id}>
                  <td>{org.name}</td>
                  <td>{org.domain || '-'}</td>
                  <td>{org.is_active ? 'Active' : 'Inactive'}</td>
                  <td>
                    <button type="button" className="ghost" onClick={() => handleSelectOrg(org)}>Edit</button>
                    <button type="button" className="ghost" onClick={() => handleDeactivateOrg(org.id)}>Deactivate</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {selectedOrgId ? (
          <form className="form-grid" onSubmit={handleUpdateOrg} style={{ marginBottom: '1rem' }}>
            <div className="form-field">
              <label>Organization name</label>
              <input value={orgEditForm.name} onChange={handleFormChange(setOrgEditForm)('name')} required />
            </div>
            <div className="form-field">
              <label>Domain</label>
              <input value={orgEditForm.domain} onChange={handleFormChange(setOrgEditForm)('domain')} />
            </div>
            <div className="form-field">
              <label>Status</label>
              <select value={orgEditForm.is_active ? 'true' : 'false'} onChange={(event) => setOrgEditForm((prev) => ({ ...prev, is_active: event.target.value === 'true' }))}>
                <option value="true">Active</option>
                <option value="false">Inactive</option>
              </select>
            </div>
            <div className="form-field">
              <button type="submit">Save Organization</button>
            </div>
          </form>
        ) : null}
        <form className="form-grid" onSubmit={handleCreateOrg}>
          <div className="form-field">
            <label>Name</label>
            <input value={orgForm.name} onChange={handleFormChange(setOrgForm)('name')} required />
          </div>
          <div className="form-field">
            <label>Domain (optional)</label>
            <input value={orgForm.domain} onChange={handleFormChange(setOrgForm)('domain')} />
          </div>
          <div className="form-field">
            <button type="submit">Create Organization</button>
          </div>
        </form>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>AD Configuration</h3>
        <p className="muted">Configure AD/LDAP connection and sync settings.</p>
        {adConfigMessage ? <div className="banner">{adConfigMessage}</div> : null}
        <form className="form-grid" onSubmit={handleSaveAdConfig}>
          <div className="form-field form-field-full">
            <strong>Server Connection</strong>
          </div>
          <div className="form-field">
            <label>Server Name</label>
            <input value={adConfigForm.server_name} onChange={handleAdConfigChange('server_name')} required />
          </div>
          <div className="form-field">
            <label>Port</label>
            <input type="number" min="1" max="65535" value={adConfigForm.server_port} onChange={handleAdConfigChange('server_port')} required />
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={adConfigForm.use_ssl} onChange={handleAdConfigChange('use_ssl')} /> Use SSL/TLS
            </label>
          </div>

          <div className="form-field form-field-full">
            <strong>Service Account</strong>
          </div>
          <div className="form-field">
            <label>Bind Username</label>
            <input value={adConfigForm.bind_username} onChange={handleAdConfigChange('bind_username')} required />
          </div>
          <div className="form-field">
            <label>Bind Password</label>
            <input type="password" value={adConfigForm.bind_password} onChange={handleAdConfigChange('bind_password')} required />
          </div>

          <div className="form-field form-field-full">
            <strong>User Search</strong>
          </div>
          <div className="form-field">
            <label>Search Base DN</label>
            <input value={adConfigForm.search_base} onChange={handleAdConfigChange('search_base')} required />
          </div>
          <div className="form-field">
            <label>Search Filter</label>
            <input value={adConfigForm.search_filter} onChange={handleAdConfigChange('search_filter')} />
          </div>

          <div className="form-field form-field-full">
            <strong>Attribute Mapping</strong>
          </div>
          <div className="form-field">
            <label>Username Attribute</label>
            <input value={adConfigForm.username_attribute} onChange={handleAdConfigChange('username_attribute')} />
          </div>
          <div className="form-field">
            <label>Email Attribute</label>
            <input value={adConfigForm.email_attribute} onChange={handleAdConfigChange('email_attribute')} />
          </div>
          <div className="form-field">
            <label>First Name Attribute</label>
            <input value={adConfigForm.first_name_attribute} onChange={handleAdConfigChange('first_name_attribute')} />
          </div>
          <div className="form-field">
            <label>Last Name Attribute</label>
            <input value={adConfigForm.last_name_attribute} onChange={handleAdConfigChange('last_name_attribute')} />
          </div>
          <div className="form-field">
            <label>Phone Attribute</label>
            <input value={adConfigForm.phone_attribute} onChange={handleAdConfigChange('phone_attribute')} />
          </div>

          <div className="form-field form-field-full">
            <strong>Group Mapping (Optional)</strong>
          </div>
          <div className="form-field">
            <label>Group Base DN</label>
            <input value={adConfigForm.group_base} onChange={handleAdConfigChange('group_base')} />
          </div>
          <div className="form-field">
            <label>Group Member Attribute</label>
            <input value={adConfigForm.group_member_attribute} onChange={handleAdConfigChange('group_member_attribute')} />
          </div>

          <div className="form-field form-field-full">
            <strong>Sync Settings</strong>
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={adConfigForm.auto_create_users} onChange={handleAdConfigChange('auto_create_users')} /> Auto Create Users
            </label>
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={adConfigForm.auto_update_users} onChange={handleAdConfigChange('auto_update_users')} /> Auto Update Users
            </label>
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={adConfigForm.auto_disable_missing_users} onChange={handleAdConfigChange('auto_disable_missing_users')} /> Auto Disable Missing Users
            </label>
          </div>
          <div className="form-field">
            <label>
              <input type="checkbox" checked={adConfigForm.is_enabled} onChange={handleAdConfigChange('is_enabled')} /> Enable AD Sync
            </label>
          </div>

          <div className="form-field form-field-full">
            <button type="submit" disabled={adConfigBusy}>Save Configuration</button>
            <button type="button" className="ghost" onClick={handleTestAdConnection} disabled={adConfigBusy || !adConfig?.id}>Test Connection</button>
            <button
              type="button"
              className="ghost"
              onClick={handleSyncAdNow}
              disabled={adConfigBusy || !adConfig?.id || !adConfig?.is_enabled || !adConfig?.is_configured}
            >
              Sync Now
            </button>
          </div>
        </form>

        {adConfig ? (
          <div className="split-grid" style={{ marginTop: '1rem' }}>
            <div>
              <strong>Last Sync</strong>
              <div>{adConfig.last_sync_at ? new Date(adConfig.last_sync_at).toLocaleString() : 'Never'}</div>
            </div>
            <div>
              <strong>Status</strong>
              <div>{adConfig.last_sync_status || 'unknown'}</div>
            </div>
            <div>
              <strong>Config Complete</strong>
              <div>{adConfig.is_configured ? 'Yes' : 'No'}</div>
            </div>
            <div>
              <strong>Enabled</strong>
              <div>{adConfig.is_enabled ? 'Yes' : 'No'}</div>
            </div>
          </div>
        ) : null}

        {adConfig?.last_sync_error ? (
          <div className="banner" style={{ marginTop: '1rem' }}>{adConfig.last_sync_error}</div>
        ) : null}
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>AD Sync History</h3>
        <div className="table">
          <table className="table">
            <thead>
              <tr>
                <th>Started</th>
                <th>Status</th>
                <th>Created</th>
                <th>Updated</th>
                <th>Skipped</th>
                <th>Source</th>
                <th>Triggered By</th>
                <th>Error</th>
              </tr>
            </thead>
            <tbody>
              {adSyncLogs.length === 0 ? (
                <tr>
                  <td colSpan="8" className="table-empty">No sync runs yet.</td>
                </tr>
              ) : adSyncLogs.map((log) => (
                <tr key={log.id}>
                  <td>{log.started_at ? new Date(log.started_at).toLocaleString() : '-'}</td>
                  <td>{log.status}</td>
                  <td>{log.created_count ?? 0}</td>
                  <td>{log.updated_count ?? 0}</td>
                  <td>{log.skipped_count ?? 0}</td>
                  <td>{log.source || '-'}</td>
                  <td>{log.triggered_by_name || '-'}</td>
                  <td>{log.error_message || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h3>Impersonate User</h3>
        <div className="form-grid">
          <div className="form-field">
            <label>Select user</label>
            <select onChange={(event) => handleImpersonate(event.target.value)} defaultValue="">
              <option value="">Select a user</option>
              {users.map((user) => (
                <option key={user.id} value={user.id}>{user.full_name || user.email}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <h3>Module Categories</h3>
        <div className="form-grid" style={{ marginBottom: '1rem' }}>
          <div className="form-field">
            <label>Module</label>
            <select value={selectedModule} onChange={(event) => setSelectedModule(event.target.value)}>
              {MODULE_OPTIONS.map((module) => (
                <option key={module.value} value={module.value}>{module.label}</option>
              ))}
            </select>
          </div>
        </div>
        <form className="form-grid" onSubmit={handleCreateCategory}>
          <div className="form-field">
            <label>Name</label>
            <input value={categoryForm.name} onChange={handleFormChange(setCategoryForm)('name')} required />
          </div>
          <div className="form-field">
            <label>Description</label>
            <input value={categoryForm.description} onChange={handleFormChange(setCategoryForm)('description')} />
          </div>
          <div className="form-field">
            <label>Sort order</label>
            <input type="number" value={categoryForm.sortOrder} onChange={handleFormChange(setCategoryForm)('sortOrder')} />
          </div>
          <div className="form-field">
            <button type="submit">Add Category</button>
          </div>
        </form>

        <div className="table" style={{ marginTop: '1rem' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Description</th>
                <th>Active</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {categories.length === 0 ? (
                <tr>
                  <td colSpan="4" className="table-empty">No categories yet.</td>
                </tr>
              ) : categories.map((category) => (
                <tr key={category.id}>
                  <td>{category.name}</td>
                  <td>{category.description || '-'}</td>
                  <td>{category.is_active ? 'Yes' : 'No'}</td>
                  <td>
                    <button type="button" className="ghost" onClick={() => handleDeleteCategory(category.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
