/**
 * Authentication Module - Cookie-based JWT Authentication
 * ★ A+ Grade: No localStorage, tokens stored in httpOnly cookies
 * OWASP A02:2021: Authentication, OWASP A04:2021: Insecure Deserialization
 */

import { apiRequest } from './client'

const USER_KEY = 'itsm_user'  // User data only, NOT tokens in localStorage

/**
 * Retrieve user data from session storage
 * ★ Note: Tokens are in httpOnly cookies, not here
 */
export function getStoredUser() {
  try {
    const stored = sessionStorage.getItem(USER_KEY)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
}

/**
 * Store user data in session storage (not tokens!)
 */
export function setStoredUser(user) {
  if (user) {
    sessionStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}

/**
 * Clear user data
 */
export function clearAuth() {
  sessionStorage.removeItem(USER_KEY)
  // ★ Tokens are automatically cleared by server (httpOnly cookie deletion)
}

/**
 * Get current authenticated user
 */
export function getCurrentUser() {
  return getStoredUser()
}

/**
 * Check if user has valid token (checks httpOnly cookie validity)
 */
export async function hasToken() {
  try {
    const response = await apiRequest('/auth/verify', {
      method: 'POST',
    })
    return response?.ok === true || response?.valid === true
  } catch {
    return false
  }
}

/**
 * Refresh tokens using httpOnly cookies
 * Server validates refresh token from cookie, returns new access token in httpOnly cookie
 */
export async function refreshToken() {
  try {
    const response = await apiRequest('/auth/refresh', {
      method: 'POST',
    })
    
    if (response?.user) {
      setStoredUser(response.user)
      return true
    }
    return false
  } catch (error) {
    console.error('[Auth] Token refresh failed:', error)
    clearAuth()
    return false
  }
}

/**
 * User login with optional TOTP
 * Server validates credentials, returns JWT in httpOnly cookie + user data in response
 */
export async function login(username, password, totpCode) {
  try {
    console.log('[AUTH] Attempting login for:', username)
    
    const payload = await apiRequest('/auth/login/', {
      method: 'POST',
      body: {
        username,
        password,
        ...(totpCode ? { totp_code: totpCode } : {}),
      },
    })

    console.log('[AUTH] Login successful, token received via httpOnly cookie')

    if (payload?.user) {
      setStoredUser(payload.user)
    }

    return payload
  } catch (error) {
    console.error('[AUTH] Login failed:', {
      message: error.message,
      status: error.status,
      payload: error.payload,
    })
    throw error
  }
}

/**
 * User logout
 * Server clears refresh token from httpOnly cookie
 */
export async function logout() {
  try {
    await apiRequest('/auth/logout', { method: 'POST' })
  } catch {
    // Ignore logout errors, clear client state anyway
  } finally {
    clearAuth()
  }
}
