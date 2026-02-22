import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error) {
    console.error('[UI] ErrorBoundary caught:', error)
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    const { hasError } = this.state
    if (hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#f6f6f9',
          padding: '2rem'
        }}>
          <div style={{
            maxWidth: '480px',
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            boxShadow: '0 12px 30px rgba(18, 18, 32, 0.12)'
          }}>
            <h2 style={{ marginTop: 0 }}>Something went wrong</h2>
            <p style={{ color: '#444' }}>
              Please refresh the page. If the problem persists, contact the service desk.
            </p>
            <button type="button" onClick={this.handleReload}>
              Retry
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}
