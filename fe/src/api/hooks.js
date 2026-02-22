import { useCallback, useEffect, useState } from 'react'
import { apiRequest, getToken } from './client'

export function useApi(path, options = {}) {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(Boolean(options.enabled ?? true))
  const [error, setError] = useState(null)
  const requireAuth = options.requireAuth !== false

  const fetchData = useCallback(async () => {
    if (options.enabled === false) {
      return
    }
    if (requireAuth && !getToken()) {
      setIsLoading(false)
      return
    }
    setIsLoading(true)
    setError(null)
    try {
      const result = await apiRequest(path, options.requestOptions)
      setData(result)
    } catch (err) {
      setError(err)
    } finally {
      setIsLoading(false)
    }
  }, [path, options.enabled, options.requestOptions, requireAuth])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, isLoading, error, reload: fetchData }
}
