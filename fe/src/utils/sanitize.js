import DOMPurify from 'dompurify'

/**
 * Sanitize HTML content to prevent XSS attacks
 * OWASP A03:2021 - Injection Prevention
 * ISO 27001 A.14.2.5
 */
export function sanitizeHTML(html) {
  if (!html || typeof html !== 'string') {
    return ''
  }

  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 's', 'a', 'ul', 'ol', 'li',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'code', 'pre',
      'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ],
    ALLOWED_ATTR: ['href', 'title', 'target', 'rel'],
    ALLOW_DATA_ATTR: false,
    FORBID_TAGS: ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover'],
  })
}

/**
 * Sanitize plain text (strip all HTML)
 */
export function sanitizeText(text) {
  if (!text || typeof text !== 'string') {
    return ''
  }
  return DOMPurify.sanitize(text, { ALLOWED_TAGS: [] })
}

/**
 * Create safe HTML object for React dangerouslySetInnerHTML
 * Usage: <div dangerouslySetInnerHTML={createSafeHTML(userContent)} />
 */
export function createSafeHTML(html) {
  return { __html: sanitizeHTML(html) }
}
