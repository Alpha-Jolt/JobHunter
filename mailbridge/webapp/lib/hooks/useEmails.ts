'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { emailsApi, type SendEmailInput, type ScheduleEmailInput } from '@/lib/api/emails'

const STALE = 30_000 // 30s

export function useEmails(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['emails', page, limit],
    queryFn: () => emailsApi.list(page, limit),
    staleTime: STALE
  })
}

export function useInboundLogs(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['emails', 'inbound', page, limit],
    queryFn: () => emailsApi.listInbound(page, limit),
    staleTime: STALE
  })
}

export function useEmailStats() {
  return useQuery({
    queryKey: ['emails', 'stats'],
    queryFn: () => emailsApi.stats(),
    staleTime: STALE
  })
}

export function useEmail(id: string) {
  return useQuery({
    queryKey: ['emails', id],
    queryFn: () => emailsApi.getById(id),
    staleTime: STALE
  })
}

export function useScheduledEmails(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['emails', 'scheduled', page, limit],
    queryFn: () => emailsApi.listScheduled(page, limit),
    staleTime: STALE
  })
}

export function useSendEmail() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: SendEmailInput) => emailsApi.send(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['emails'] })
  })
}

export function useSendBatch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (emails: SendEmailInput[]) => emailsApi.sendBatch(emails),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['emails'] })
  })
}

export function useScheduleEmail() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: ScheduleEmailInput) => emailsApi.schedule(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['emails', 'scheduled'] })
  })
}

export function useCancelScheduled() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => emailsApi.cancelScheduled(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['emails', 'scheduled'] })
  })
}
