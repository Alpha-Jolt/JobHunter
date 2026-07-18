import { apiClient } from './client'
import type { EmailLog, ScheduledEmail, IncomingEmailLog } from '@/lib/types/api'

export interface EmailStats {
  total: number
  sent: number
  failed: number
  queued: number
  today: number
}

export interface SendEmailInput {
  credential_id: string
  to_email: string
  subject?: string
  html?: string
  variables?: Record<string, unknown>
  template_id?: string
  attachments?: { filename: string; url: string }[]
}

export interface ScheduleEmailInput extends SendEmailInput {
  scheduled_at: string
}

export const emailsApi = {
  send: (input: SendEmailInput) =>
    apiClient.post<{ success: boolean; email_id: string; status: string }>('/api/emails/send', input),

  sendBatch: (emails: SendEmailInput[]) =>
    apiClient.post<{ success: boolean; queued: number; email_ids: string[] }>('/api/emails/batch', { emails }),

  schedule: (input: ScheduleEmailInput) =>
    apiClient.post<{ success: boolean; scheduled_id: string; scheduled_at: string }>('/api/emails/schedule', input),

  cancelScheduled: (id: string) =>
    apiClient.delete<{ success: boolean }>(`/api/emails/schedule/${id}`),

  listScheduled: (page = 1, limit = 20) =>
    apiClient.get<{ success: boolean; scheduled: ScheduledEmail[]; total: number; page: number; limit: number }>(
      `/api/emails/schedule?page=${page}&limit=${limit}`
    ),

  list: (page = 1, limit = 20) =>
    apiClient.get<{ success: boolean; emails: EmailLog[]; total: number; page: number; limit: number }>(
      `/api/emails?page=${page}&limit=${limit}`
    ),

  listInbound: (page = 1, limit = 20) =>
    apiClient.get<{ success: boolean; logs: IncomingEmailLog[]; total: number; page: number; limit: number }>(
      `/api/emails/inbound?page=${page}&limit=${limit}`
    ),

  stats: () =>
    apiClient.get<{ success: boolean; stats: EmailStats }>('/api/emails/stats'),

  getById: (id: string) =>
    apiClient.get<{ success: boolean; email: EmailLog }>(`/api/emails/${id}`)
}
