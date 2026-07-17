'use client'

import { useEffect } from 'react'
import { useAuthStore } from '@/lib/store/authStore'
import { getMe } from '@/lib/api/auth'

export function useAuth() {
  const { user, isAuthenticated, setUser, clear } = useAuthStore()

  useEffect(() => {
    if (!isAuthenticated) {
      getMe().then(setUser).catch(() => clear())
    }
  }, [isAuthenticated, setUser, clear])

  return { user, isAuthenticated }
}
