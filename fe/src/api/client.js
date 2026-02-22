/**
 * API Client - Secure HTTP Client with Cookie-based JWT Authentication
 * Stores tokens in httpOnly cookies (XSS protected)
 * OWASP A03:2021, NIST SP 800-63B
 */

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || `${window.location.origin}/api/v1`

export function getApiBaseUrl() {
  return API_BASE_URL.replace(/\/$/, '')
}

/**
 * Helper: Extract CSRF token from cookies
 * Required for Django CSRF protection on state-changing requests
 */
function getCsrfToken() {
  // Django's default CSRF cookie name
  const name = 'csrftoken'
  const cookies = document.cookie.split(';')
  for (const cookie of cookies) {
    const [key, value] = cookie.trim().split('=')
    if (key === name) {
      return decodeURIComponent(value)
    }
  }
  return null
}

function buildUrl(path) {
  if (!path) {
    return getApiBaseUrl()
  }
  if (path.startsWith('http')) {
    return path
  }
  return `${getApiBaseUrl()}${path.startsWith('/') ? '' : '/'}${path}`
}

/**
 * Make secure API request with httpOnly JWT cookies
 * 
 * Tokens are automatically sent via httpOnly cookies (secure)
 * CSRF token added for state-changing requests
 * 
 * @param {string} path - API endpoint path
 * @param {object} options - Request options (method, body, headers, etc)
 * @returns {Promise} API response
 */
export async function apiRequest(path, options = {}) {
  const url = buildUrl(path)
  const retries = Number.isInteger(options.retries) ? options.retries : 1

  const headers = {
    Accept: 'application/json',
    ...(options.headers || {}),
  }

  let body = options.body
  if (body && typeof body === 'object' && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }

  // ★ A+: Add CSRF token for state-changing requests
  const method = (options.method || 'GET').toUpperCase()
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken
    }
  }

  let attempt = 0
  while (attempt <= retries) {
    try {
      console.log(`[API] ${method} ${url}`, { headers, body: options.body })

      const response = await fetch(url, {
        method,
        headers,
        body,
        credentials: 'include',  // ★ CRITICAL: Send httpOnly cookies + CSRF token
      })

      console.log(`[API] Response status: ${response.status}`)

      const contentType = response.headers.get('content-type') || ''
      const hasJson = contentType.includes('application/json')
      const payload = hasJson ? await response.json() : await response.text()

      console.log(`[API] Response payload:`, payload)

      if (!response.ok) {
        console.error(`[API] Error ${response.status}:`, payload)
        const error = new Error('API request failed')
        error.status = response.status
        error.payload = payload
        throw error
      }

      return payload
    } catch (error) {
      const status = error?.status
      const shouldRetry = !status || status >= 500
      attempt += 1
      if (!shouldRetry || attempt > retries) {
        console.error(`[API] Network error: ${error.message}`)
        throw error
      }
      await new Promise((resolve) => setTimeout(resolve, 500))
    }
  }
}
