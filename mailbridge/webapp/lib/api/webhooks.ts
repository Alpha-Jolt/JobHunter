import { apiClient } from './client'
import type { Webhook, WebhookDelivery, WebhookEvent } from '@/lib/types/api'

export interface CreateWebhookInput {
  url: string
  events: WebhookEvent[]
  secret: string
}

export const webhooksApi = {
  list: () =>
    apiClient.get<{ success: boolean; webhooks: Webhook[] }>('/api/webhooks'),

  create: (input: CreateWebhookInput) =>
    apiClient.post<{ success: boolean; webhook_id: string; secret: string }>('/api/webhooks', input),

  update: (id: string, input: Partial<Pick<CreateWebhookInput, 'url' | 'events'> & { is_active: boolean }>) =>
    apiClient.put<{ success: boolean; webhook: Webhook }>(`/api/webhooks/${id}`, input),

  remove: (id: string) =>
    apiClient.delete<{ success: boolean }>(`/api/webhooks/${id}`),

  test: (id: string) =>
    apiClient.post<{ success: boolean; delivery_id: string }>(`/api/webhooks/${id}/test`),

  getDeliveries: (id: string, page = 1, limit = 20) =>
    apiClient.get<{ success: boolean; deliveries: WebhookDelivery[]; total: number; page: number; limit: number }>(
      `/api/webhooks/${id}/deliveries?page=${page}&limit=${limit}`
    )
}
