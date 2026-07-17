'use client'

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { webhooksApi, type CreateWebhookInput } from '@/lib/api/webhooks'
import type { WebhookEvent } from '@/lib/types/api'

const STALE = 5 * 60_000 // 5min

export function useWebhooks() {
  return useQuery({
    queryKey: ['webhooks'],
    queryFn: () => webhooksApi.list(),
    staleTime: STALE
  })
}

export function useWebhookDeliveries(id: string, page = 1) {
  return useQuery({
    queryKey: ['webhooks', id, 'deliveries', page],
    queryFn: () => webhooksApi.getDeliveries(id, page),
    staleTime: 30_000
  })
}

export function useCreateWebhook() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: CreateWebhookInput) => webhooksApi.create(input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['webhooks'] })
  })
}

export function useUpdateWebhook() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, input }: { id: string; input: Partial<{ url: string; events: WebhookEvent[]; is_active: boolean }> }) =>
      webhooksApi.update(id, input),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['webhooks'] })
  })
}

export function useDeleteWebhook() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => webhooksApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['webhooks'] })
  })
}

export function useTestWebhook() {
  return useMutation({
    mutationFn: (id: string) => webhooksApi.test(id)
  })
}
