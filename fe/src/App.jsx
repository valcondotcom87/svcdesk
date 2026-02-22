import { useEffect, useState } from 'react'
import { Routes, Route, useLocation, useNavigate } from 'react-router-dom'
import './App.css'
import Dashboard from './pages/Dashboard.jsx'
import Incidents from './pages/Incidents.jsx'
import ServiceRequests from './pages/ServiceRequests.jsx'
import Problems from './pages/Problems.jsx'
import Changes from './pages/Changes.jsx'
import CMDB from './pages/CMDB.jsx'
import Assets from './pages/Assets.jsx'
import AssetDashboard from './pages/AssetDashboard.jsx'
import Knowledge from './pages/Knowledge.jsx'
import SlaReports from './pages/SlaReports.jsx'
import ExecutiveDashboard from './pages/ExecutiveDashboard.jsx'
import Admin from './pages/Admin.jsx'
import CreateTicketModal from './components/CreateTicketModal.jsx'
import LoginForm from './components/LoginForm.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'
import OfflineBanner from './components/OfflineBanner.jsx'
import { login, logout, getCurrentUser, hasToken } from './api/auth.js'

const navItems = [
  { label: 'Dashboard', path: '/', requiresAuth: false },
  { label: 'Incidents', path: '/incidents', requiresAuth: true },
  { label: 'Service Requests', path: '/requests', requiresAuth: true },
  { label: 'Problems', path: '/problems', requiresAuth: true },
  { label: 'Changes', path: '/changes', requiresAuth: true },
  { label: 'CMDB', path: '/cmdb', requiresAuth: true },
  { label: 'Asset Dashboard', path: '/assets-dashboard', requiresAuth: true },
  { label: 'Assets', path: '/assets', requiresAuth: true },
  { label: 'Knowledge', path: '/knowledge', requiresAuth: false },
  { label: 'SLA & Reports', path: '/sla-reports', requiresAuth: false },
  { label: 'Executive', path: '/executive-dashboard', requiresAuth: false },
  { label: 'Admin', path: '/admin', requiresAuth: true, requiresAdmin: true },
]

const roleAccess = {
  end_user: ['/', '/incidents', '/requests', '/knowledge'],
}

function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const [authStatus, setAuthStatus] = useState('unknown')
  const [authError, setAuthError] = useState('')
  const [currentUser, setCurrentUser] = useState(getCurrentUser())
  const [showLoginForm, setShowLoginForm] = useState(false)
  const [createModalOpen, setCreateModalOpen] = useState(false)
  const [createModalType, setCreateModalType] = useState('incident')

  useEffect(() => {
    const tokenAvailable = hasToken()
    if (tokenAvailable) {
      setAuthStatus('ready')
    } else {
      setAuthStatus('missing')
    }
  }, [])

  const handleLogin = (username, password, totpCode) => {
    setAuthStatus('loading')
    setAuthError('')
    login(username, password, totpCode)
      .then((payload) => {
        console.log('[APP] Login successful')
        setCurrentUser(payload?.user || null)
        setAuthStatus('ready')
        setAuthError('')
        setShowLoginForm(false)
      })
      .catch((error) => {
        console.error('[APP] Login failed:', error)
        setAuthStatus('error')
        const errorMsg = error.payload?.error || error.payload?.message || error.message || 'Invalid username or password.'
        setAuthError(errorMsg)
      })
  }

  const handleLogout = () => {
    logout()
    setCurrentUser(null)
    setAuthStatus('missing')
    setShowLoginForm(false)
  }

  const openCreateModal = (type = 'incident') => {
    setCreateModalType(type)
    setCreateModalOpen(true)
  }

  const closeCreateModal = () => {
    setCreateModalOpen(false)
  }

  const userName = currentUser?.first_name
    ? `${currentUser.first_name} ${currentUser.last_name || ''}`.trim()
    : currentUser?.email || 'Guest'
  const roleLabels = {
    end_user: 'End User',
    asset_manager: 'Asset Manager',
    engineer: 'Engineer',
    agent: 'Agent',
    manager: 'Manager',
    admin: 'Administrator',
  }
  const userRole = currentUser
    ? currentUser.is_superuser
      ? 'Super Admin'
      : roleLabels[currentUser.role] || 'User'
    : 'Not signed in'

  const isAuthenticated = authStatus === 'ready'
  const isAdmin = Boolean(currentUser && (currentUser.is_superuser || currentUser.role === 'admin'))

  const canAccessAdmin = isAdmin

  const canAccessPath = (path, requiresAuth = true, requiresAdmin = false) => {
    if (requiresAuth && !isAuthenticated) {
      return false
    }
    if (requiresAdmin && !isAdmin) {
      return false
    }
    if (!currentUser) {
      return !requiresAuth
    }
    if (currentUser.is_superuser) {
      return true
    }
    const allowed = roleAccess[currentUser.role]
    if (!allowed) {
      return true
    }
    return allowed.includes(path)
  }

  // Filter navigation items based on authentication status
  const visibleNavItems = navItems.filter((item) => (
    canAccessPath(item.path, item.requiresAuth ?? true, item.requiresAdmin)
  ))

  const dashboardElement = (
    <Dashboard showLogin={authStatus !== 'ready'} onLoginClick={() => setShowLoginForm(true)} />
  )

  if (authStatus !== 'ready' && showLoginForm) {
    return (
      <ErrorBoundary>
        <OfflineBanner />
        <LoginForm
          onLogin={handleLogin}
          onBack={() => setShowLoginForm(false)}
          error={authStatus === 'error' ? authError : ''}
          loading={authStatus === 'loading'}
        />
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <OfflineBanner />
      <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">ITSM</div>
          <div className="brand-text">Service Desk</div>
        </div>
        <nav className="nav">
          {visibleNavItems.map((item) => (
            <button
              key={item.path}
              className={`nav-item${location.pathname === item.path ? ' active' : ''}`}
              onClick={() => navigate(item.path)}
              type="button"
            >
              {item.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="status-pill">Online</div>
          <div className="muted">Region: APAC</div>
        </div>
      </aside>

      <div className="main-area">
        <header className="topbar">
          <div className="search">
            <input placeholder="Search tickets, CIs, users" aria-label="Global search" />
          </div>
          <div className="topbar-actions">
            <button className="ghost" type="button">Notifications</button>
            {authStatus === 'ready' ? (
              <button className="ghost" type="button" onClick={() => openCreateModal('incident')}>Create Ticket</button>
            ) : null}
            <div className="user-chip">
              <div className="avatar">AM</div>
              <div>
                <div className="user-name">{userName}</div>
                <div className="muted">{userRole}</div>
              </div>
            </div>
            {authStatus === 'ready' ? (
              <button className="ghost" type="button" onClick={handleLogout}>Sign Out</button>
            ) : (
              <button className="ghost" type="button" onClick={() => setShowLoginForm(true)}>Login</button>
            )}
          </div>
        </header>

        <main className="content">
          <Routes>
            <Route path="/" element={dashboardElement} />
            <Route
              path="/incidents"
              element={canAccessPath('/incidents') ? <Incidents onCreateTicket={openCreateModal} /> : dashboardElement}
            />
            <Route
              path="/requests"
              element={canAccessPath('/requests')
                ? <ServiceRequests onCreateTicket={openCreateModal} currentUser={currentUser} />
                : dashboardElement}
            />
            <Route
              path="/problems"
              element={canAccessPath('/problems') ? <Problems onCreateTicket={openCreateModal} /> : dashboardElement}
            />
            <Route
              path="/changes"
              element={canAccessPath('/changes') ? <Changes onCreateTicket={openCreateModal} /> : dashboardElement}
            />
            <Route path="/cmdb" element={canAccessPath('/cmdb') ? <CMDB /> : dashboardElement} />
            <Route
              path="/assets-dashboard"
              element={canAccessPath('/assets-dashboard') ? <AssetDashboard /> : dashboardElement}
            />
            <Route
              path="/assets"
              element={canAccessPath('/assets') ? <Assets onCreateTicket={openCreateModal} /> : dashboardElement}
            />
            <Route path="/knowledge" element={canAccessPath('/knowledge', false) ? <Knowledge /> : dashboardElement} />
            <Route path="/sla-reports" element={canAccessPath('/sla-reports', false) ? <SlaReports /> : dashboardElement} />
            <Route
              path="/executive-dashboard"
              element={canAccessPath('/executive-dashboard', false) ? <ExecutiveDashboard /> : dashboardElement}
            />
            <Route path="/admin" element={canAccessPath('/admin', true, true) ? <Admin /> : dashboardElement} />
          </Routes>
        </main>
      </div>

        <CreateTicketModal
          open={createModalOpen}
          type={createModalType}
          onClose={closeCreateModal}
          currentUser={currentUser}
        />
      </div>
    </ErrorBoundary>
  )
}

export default App
