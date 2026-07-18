'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '@/lib/api/admin'
import type { FlatRole } from '@/lib/types/api'

const STALE = 2 * 60_000 // 2min

export function useAdminUsers() {
  return useQuery({
    queryKey: ['admin', 'users'],
    queryFn: () => adminApi.listUsers(),
    staleTime: STALE
  })
}

export function useInviteUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ email, role }: { email: string; role: FlatRole }) =>
      adminApi.inviteUser(email, role),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] })
  })
}

export function useChangeRole() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: FlatRole }) =>
      adminApi.changeRole(userId, role),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] })
  })
}

export function useRemoveUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (userId: string) => adminApi.removeUser(userId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin', 'users'] })
  })
}
