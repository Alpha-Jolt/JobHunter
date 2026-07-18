import { apiClient } from './client'
import type { AuthUser } from '@/lib/types/api'

export interface LoginInput { email: string; password: string }
export interface RegisterInput { email: string; password: string; workspace_name: string }

// Called from Next.js API routes (server-side) — passes token from cookie
export async function loginBackend(input: LoginInput, token?: string) {
  return apiClient.post<{ success: boolean; token: string; expires_at: string }>(
    '/auth/login', input, { token }
  )
}

export async function registerBackend(input: RegisterInput, token?: string) {
  return apiClient.post<{ success: boolean; token: string; user_id: string; workspace_id: string; expires_at: string }>(
    '/auth/register', input, { token }
  )
}

export async function logoutBackend(token: string) {
  return apiClient.post<{ success: boolean }>('/auth/logout', {}, { token })
}

export async function refreshBackend(token: string) {
  return apiClient.post<{ success: boolean; token: string; expires_at: string }>(
    '/auth/refresh', { token }, {}
  )
}

export async function upgradeBackend(token: string) {
  return apiClient.post<{ success: boolean; token: string; expires_at: string }>(
    '/auth/upgrade', {}, { token }
  )
}

// Client-side: calls Next.js API route /api/auth/me
export async function getMe(): Promise<AuthUser> {
  const res = await fetch('/api/auth/me', {
    credentials: 'include',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  if (!res.ok) throw new Error('Not authenticated')
  const data = await res.json()
  return data.user as AuthUser
}
