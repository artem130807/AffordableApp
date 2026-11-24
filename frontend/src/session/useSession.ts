import { useCallback, useEffect, useState } from 'react'
import { authApi } from '../api/affordable'
import { apiClient } from '../api/client'
import type { User } from '../types'

export function useSession() {
  const [user, setUser] = useState<User | null>(null)
  const [isRestoring, setIsRestoring] = useState(apiClient.hasSession())

  useEffect(() => {
    if (!apiClient.hasSession()) return
    void authApi.me()
      .then(setUser)
      .catch(() => apiClient.clearSession())
      .finally(() => setIsRestoring(false))
  }, [])

  const logout = useCallback(async () => {
    try {
      await authApi.logout()
    } finally {
      setUser(null)
    }
  }, [])

  return { user, setUser, logout, isRestoring }
}
