'use client'

import { useAuth } from '@/lib/hooks/useAuth'
import type { FlatRole } from '@/lib/types/api'

interface Props { role: FlatRole; children: React.ReactNode; fallback?: React.ReactNode }

export function RoleGuard({ role, children, fallback = null }: Props) {
  const { user } = useAuth()
  if (!user || user.role !== role) return <>{fallback}</>
  return <>{children}</>
}
