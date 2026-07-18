import { apiClient } from './client'
import type { EmailTemplate, EmailTemplateVersion, ValidationRules } from '@/lib/types/api'

export interface CreateTemplateInput {
  name: string
  subject: string
  html: string
  variables?: string[]
  validation_rules?: ValidationRules
}

export const templatesApi = {
  list: () =>
    apiClient.get<{ success: boolean; templates: EmailTemplate[] }>('/api/templates'),

  create: (input: CreateTemplateInput) =>
    apiClient.post<{ success: boolean; template: EmailTemplate }>('/api/templates', input),

  update: (id: string, input: Partial<CreateTemplateInput>) =>
    apiClient.put<{ success: boolean; template: EmailTemplate }>(`/api/templates/${id}`, input),

  remove: (id: string) =>
    apiClient.delete<{ success: boolean }>(`/api/templates/${id}`),

  getVersions: (id: string, page = 1, limit = 20) =>
    apiClient.get<{ success: boolean; versions: EmailTemplateVersion[]; total: number; page: number; limit: number }>(
      `/api/templates/${id}/versions?page=${page}&limit=${limit}`
    ),

  rollback: (id: string, version: number) =>
    apiClient.post<{ success: boolean; template: EmailTemplate }>(`/api/templates/${id}/rollback`, { version })
}
