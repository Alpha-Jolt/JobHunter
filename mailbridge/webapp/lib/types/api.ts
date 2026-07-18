// Frontend-facing types mirroring backend domain types

export type WorkspaceTier = 'free' | 'pro' | 'enterprise'
export type FlatRole = 'owner' | 'member'
export type ProviderType = 'gmail' | 'outlook' | 'smtp'
export type EmailStatus = 'queued' | 'sent' | 'failed' | 'bounced'
export type WebhookEvent = 'email.sent' | 'email.failed' | 'email.bounced'
export type WebhookDeliveryStatus = 'pending' | 'delivered' | 'failed'
export type ScheduledEmailStatus = 'pending' | 'queued' | 'cancelled'

export interface AuthUser {
  user_id: string
  email: string
  workspace_id: string
  tier: WorkspaceTier
  role: FlatRole
}

export interface Credential {
  credential_id: string
  workspace_id: string
  provider_type: ProviderType
  from_email: string
  is_active: boolean
  last_used_at: string | null
  created_at: string
}

export interface EmailLog {
  email_id: string
  workspace_id: string
  credential_id: string | null
  to_email: string
  from_email: string
  subject: string
  template_id: string | null
  provider_message_id: string | null
  status: EmailStatus
  sent_at: string | null
  retry_count: number
  created_at: string
}

export interface IncomingEmailLog {
  log_id: string
  workspace_id: string
  credential_id: string
  from_address: string
  subject: string | null
  received_at: string
  created_at: string
}

export interface ValidationRules {
  required?: string[]
  maxLength?: Record<string, number>
  pattern?: Record<string, string>
}

export interface EmailTemplate {
  template_id: string
  workspace_id: string
  name: string
  subject: string
  html: string
  variables: string[]
  validation_rules: ValidationRules
  version: number
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface EmailTemplateVersion {
  version_id: string
  template_id: string
  version: number
  name: string
  subject: string
  html: string
  variables: string[]
  validation_rules: ValidationRules
  snapshotted_by: string | null
  snapshotted_at: string
}

export interface ScheduledEmail {
  scheduled_id: string
  workspace_id: string
  credential_id: string
  to_email: string
  subject: string
  scheduled_at: string
  status: ScheduledEmailStatus
  created_at: string
}

export interface Webhook {
  webhook_id: string
  workspace_id: string
  url: string
  events: WebhookEvent[]
  is_active: boolean
  created_at: string
}

export interface WebhookDelivery {
  delivery_id: string
  webhook_id: string
  email_id: string | null
  event: WebhookEvent
  status: WebhookDeliveryStatus
  attempts: number
  next_retry_at: string | null
  last_error: string | null
  delivered_at: string | null
  created_at: string
}

export interface WorkspaceUser {
  user_id: string
  email: string
  role: FlatRole
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  success: boolean
  total: number
  page: number
  limit: number
  data: T[]
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
  }
}
