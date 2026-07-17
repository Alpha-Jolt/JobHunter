// Core domain types shared across all Mail-Bridge services

export type WorkspaceTier = 'free' | 'pro' | 'enterprise'
export type FlatRole = 'owner' | 'member'
export type EnterpriseRole = 'system-admin' | 'operational-admin' | 'admin' | 'user'
export type ProviderType = 'gmail' | 'outlook' | 'smtp'
export type WebhookEvent = 'email.sent' | 'email.failed' | 'email.bounced'
export type ScheduledEmailStatus = 'pending' | 'queued' | 'cancelled'
export type WebhookDeliveryStatus = 'pending' | 'delivered' | 'failed'
export type EmailStatus = 'queued' | 'sent' | 'failed' | 'bounced'

export interface Workspace {
  workspace_id: string
  name: string
  tier: WorkspaceTier
  settings: Record<string, unknown>
  created_at: Date
}

export interface User {
  user_id: string
  email: string
  password_hash: string
  workspace_id: string | null
  role: FlatRole
  created_at: Date
  updated_at: Date
  deleted_at: Date | null
}

export interface WorkspaceRole {
  id: string
  workspace_id: string
  user_id: string
  role: EnterpriseRole
  scope: Record<string, unknown>
  assigned_at: Date
}

export interface Credential {
  credential_id: string
  workspace_id: string
  provider_type: ProviderType
  from_email: string
  encrypted_value: string
  encryption_key_id: string
  is_active: boolean
  last_used_at: Date | null
  metadata: Record<string, unknown>
  created_at: Date
}

export interface EmailTemplate {
  template_id: string
  workspace_id: string
  name: string
  subject: string
  html: string
  variables: string[]
  validation_rules: ValidationRules
  created_by: string | null
  version: number
  created_at: Date
  updated_at: Date
}

export interface ValidationRules {
  required?: string[]
  maxLength?: Record<string, number>
  pattern?: Record<string, string>
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
  snapshotted_at: Date
}

export interface ScheduledEmail {
  scheduled_id: string
  workspace_id: string
  credential_id: string
  to_email: string
  subject: string
  html: string
  variables: Record<string, unknown>
  template_id: string | null
  scheduled_at: Date
  status: ScheduledEmailStatus
  created_by: string | null
  created_at: Date
}

export interface Webhook {
  webhook_id: string
  workspace_id: string
  url: string
  events: WebhookEvent[]
  is_active: boolean
  created_by: string | null
  created_at: Date
}

export interface WebhookDelivery {
  delivery_id: string
  webhook_id: string
  email_id: string | null
  event: WebhookEvent
  payload: Record<string, unknown>
  status: WebhookDeliveryStatus
  attempts: number
  next_retry_at: Date | null
  last_error: string | null
  delivered_at: Date | null
  created_at: Date
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
  sent_at: Date | null
  retry_count: number
  metadata: Record<string, unknown>
  created_at: Date
}

export interface ApiKey {
  api_key_id: string
  workspace_id: string
  key_hash: string
  name: string
  created_by: string | null
  last_used_at: Date | null
  expires_at: Date | null
  scopes: string[]
  created_at: Date
}

// JWT payload attached to req.user after authentication
export interface AuthUser {
  user_id: string
  workspace_id: string
  tier: WorkspaceTier
  role: FlatRole | EnterpriseRole
}

// Email job pushed to Redis queue
export interface EmailJob {
  jobId: string
  emailLogId: string
  credentialId: string
  workspaceId: string
  to: string
  from: string
  subject: string
  html: string
  attachments?: { filename: string; url: string }[]
}

// Augment Express Request with authenticated user
declare global {
  // eslint-disable-next-line @typescript-eslint/no-namespace
  namespace Express {
    interface Request {
      user?: AuthUser
      id?: string
      apiKeyScopes?: string[]
    }
  }
}
