'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { credentialsApi, type SmtpInput } from '@/lib/api/credentials'

const STALE = 5 * 60_000 // 5min

export function useCredentials() {
  return useQuery({
    queryKey: ['credentials'],
    queryFn: () => credentialsApi.list(),
    staleTime: STALE
  })
}

export function useAddSmtp() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: SmtpInput) => credentialsApi.addSmtp(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['credentials'] })
  })
}

export function useRemoveCredential() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => credentialsApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['credentials'] })
  })
}

export function useTestCredential() {
  return useMutation({
    mutationFn: (id: string) => credentialsApi.test(id)
  })
}
