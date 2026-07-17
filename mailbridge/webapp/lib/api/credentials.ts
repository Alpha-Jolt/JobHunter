import { apiClient } from './client'
import type { Credential } from '@/lib/types/api'

export interface SmtpInput {
  from_email: string
  host: string
  port: number
  secure: boolean
  user: string
  pass: string
}

export const credentialsApi = {
  list: () =>
    apiClient.get<{ success: boolean; credentials: Credential[] }>('/api/credentials'),

  addSmtp: (input: SmtpInput) =>
    apiClient.post<{ success: boolean; credential_id: string; from_email: string; provider_type: string }>(
      '/api/credentials/smtp', input
    ),

  gmailConnectUrl: () =>
    apiClient.get<{ success: boolean; url: string }>('/api/credentials/gmail/connect'),

  outlookConnectUrl: () =>
    apiClient.get<{ success: boolean; url: string }>('/api/credentials/outlook/connect'),

  remove: (id: string) =>
    apiClient.delete<{ success: boolean }>(`/api/credentials/${id}`),

  test: (id: string) =>
    apiClient.post<{ success: boolean; message: string }>(`/api/credentials/${id}/test`)
}
