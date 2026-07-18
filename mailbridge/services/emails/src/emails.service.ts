import { Pool } from 'pg'
import axios from 'axios'
import { renderTemplate } from './composer'
import { GmailProvider } from './providers/gmailProvider'
import { SmtpProvider } from './providers/smtpProvider'
import { OutlookProvider } from './providers/outlookProvider'
import {
  enqueue, dequeue, MAX_RETRIES, logger, getRedisClient,
  NotFoundError, ValidationError,
  EmailLog, EmailJob, ValidationRules
} from '@mail-bridge/shared'
import { EmailsConfig } from './config'
import { decrypt } from './credentialManager'

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
  scheduled_at: string // ISO8601
}

export class EmailsService {
  constructor(
    private readonly pool: Pool,
    private readonly config: EmailsConfig
  ) {}

  // Validate variables against template validation_rules
  private validateVariables(variables: Record<string, unknown>, rules: ValidationRules): void {
    const errors: string[] = []

    for (const field of rules.required ?? []) {
      if (variables[field] === undefined || variables[field] === null || variables[field] === '') {
        errors.push(`Required variable missing: ${field}`)
      }
    }

    for (const [field, max] of Object.entries(rules.maxLength ?? {})) {
      const val = variables[field]
      if (typeof val === 'string' && val.length > max) {
        errors.push(`Variable ${field} exceeds maxLength ${max}`)
      }
    }

    for (const [field, pattern] of Object.entries(rules.pattern ?? {})) {
      const val = variables[field]
      if (typeof val === 'string' && !new RegExp(pattern).test(val)) {
        errors.push(`Variable ${field} does not match pattern ${pattern}`)
      }
    }

    if (errors.length > 0) {
      throw new ValidationError(errors.join('; '), 'VALIDATION_FAILED')
    }
  }

  private async resolveTemplate(
    templateId: string,
    workspaceId: string,
    variables: Record<string, unknown>
  ): Promise<{ subject: string; html: string }> {
    const tmpl = await this.pool.query<{ subject: string; html: string; validation_rules: ValidationRules }>(
      'SELECT subject, html, validation_rules FROM email_templates WHERE template_id = $1 AND workspace_id = $2',
      [templateId, workspaceId]
    )
    if (!tmpl.rows[0]) throw new NotFoundError('Template not found')
    this.validateVariables(variables, tmpl.rows[0].validation_rules ?? {})
    return { subject: tmpl.rows[0].subject, html: tmpl.rows[0].html }
  }

  private async getCredentialFromEmail(credentialId: string, workspaceId: string): Promise<string> {
    const row = await this.pool.query<{ from_email: string }>(
      'SELECT from_email FROM credentials WHERE credential_id = $1 AND workspace_id = $2 AND is_active = TRUE',
      [credentialId, workspaceId]
    )
    if (!row.rows[0]) throw new NotFoundError('Credential not found')
    return row.rows[0].from_email
  }

  async send(input: SendEmailInput, workspaceId: string): Promise<{ email_id: string; status: string }> {
    if (!input.credential_id || !input.to_email) {
      throw new ValidationError('credential_id and to_email are required', 'INVALID_PAYLOAD')
    }

    let subject = input.subject ?? ''
    let html = input.html ?? ''

    if (input.template_id) {
      const resolved = await this.resolveTemplate(input.template_id, workspaceId, input.variables ?? {})
      subject = resolved.subject
      html = resolved.html
    }

    if (!subject || !html) throw new ValidationError('subject and html are required (or provide template_id)', 'INVALID_PAYLOAD')

    const rendered = renderTemplate(html, subject, input.variables ?? {})
    const fromEmail = await this.getCredentialFromEmail(input.credential_id, workspaceId)

    const logResult = await this.pool.query<{ email_id: string }>(
      `INSERT INTO email_logs (workspace_id, credential_id, to_email, from_email, subject, template_id, status)
       VALUES ($1, $2, $3, $4, $5, $6, 'queued') RETURNING email_id`,
      [workspaceId, input.credential_id, input.to_email, fromEmail, rendered.subject, input.template_id ?? null]
    )
    const emailLogId = logResult.rows[0].email_id

    await enqueue({
      emailLogId,
      credentialId: input.credential_id,
      workspaceId,
      to: input.to_email,
      from: fromEmail,
      subject: rendered.subject,
      html: rendered.html,
      attachments: input.attachments
    })

    return { email_id: emailLogId, status: 'queued' }
  }

  async sendBatch(
    emails: SendEmailInput[],
    workspaceId: string
  ): Promise<{ queued: number; email_ids: string[] }> {
    if (!emails.length) throw new ValidationError('emails array is empty', 'INVALID_PAYLOAD')
    if (emails.length > this.config.batchMaxSize) {
      throw new ValidationError(`Batch exceeds maximum size of ${this.config.batchMaxSize}`, 'BATCH_TOO_LARGE')
    }

    const email_ids: string[] = []
    for (const item of emails) {
      const result = await this.send(item, workspaceId)
      email_ids.push(result.email_id)
    }

    return { queued: email_ids.length, email_ids }
  }

  async scheduleEmail(
    input: ScheduleEmailInput,
    workspaceId: string,
    userId: string
  ): Promise<{ scheduled_id: string; scheduled_at: string }> {
    if (!input.credential_id || !input.to_email || !input.scheduled_at) {
      throw new ValidationError('credential_id, to_email, scheduled_at are required', 'INVALID_PAYLOAD')
    }

    const scheduledAt = new Date(input.scheduled_at)
    if (isNaN(scheduledAt.getTime()) || scheduledAt <= new Date()) {
      throw new ValidationError('scheduled_at must be a valid future UTC datetime', 'INVALID_PAYLOAD')
    }

    // Validate credential ownership
    await this.getCredentialFromEmail(input.credential_id, workspaceId)

    let subject = input.subject ?? ''
    let html = input.html ?? ''

    if (input.template_id) {
      const resolved = await this.resolveTemplate(input.template_id, workspaceId, input.variables ?? {})
      subject = resolved.subject
      html = resolved.html
    }

    if (!subject || !html) throw new ValidationError('subject and html are required (or provide template_id)', 'INVALID_PAYLOAD')

    const rendered = renderTemplate(html, subject, input.variables ?? {})

    const result = await this.pool.query<{ scheduled_id: string; scheduled_at: Date }>(
      `INSERT INTO scheduled_emails
         (workspace_id, credential_id, to_email, subject, html, variables, template_id, scheduled_at, created_by)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       RETURNING scheduled_id, scheduled_at`,
      [
        workspaceId, input.credential_id, input.to_email,
        rendered.subject, rendered.html, JSON.stringify(input.variables ?? {}),
        input.template_id ?? null, scheduledAt, userId
      ]
    )

    return {
      scheduled_id: result.rows[0].scheduled_id,
      scheduled_at: result.rows[0].scheduled_at.toISOString()
    }
  }

  async cancelScheduled(scheduledId: string, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      `UPDATE scheduled_emails SET status = 'cancelled'
       WHERE scheduled_id = $1 AND workspace_id = $2 AND status = 'pending'`,
      [scheduledId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('Scheduled email not found or already processed')
  }

  async listScheduled(
    workspaceId: string,
    page = 1,
    limit = 20
  ): Promise<{ scheduled: unknown[]; total: number }> {
    const offset = (page - 1) * limit
    const [rows, count] = await Promise.all([
      this.pool.query(
        `SELECT scheduled_id, to_email, subject, scheduled_at, status, created_at
         FROM scheduled_emails WHERE workspace_id = $1 AND status = 'pending'
         ORDER BY scheduled_at ASC LIMIT $2 OFFSET $3`,
        [workspaceId, limit, offset]
      ),
      this.pool.query<{ count: string }>(
        `SELECT COUNT(*) FROM scheduled_emails WHERE workspace_id = $1 AND status = 'pending'`,
        [workspaceId]
      )
    ])
    return { scheduled: rows.rows, total: parseInt(count.rows[0].count) }
  }

  async list(workspaceId: string, page = 1, limit = 20): Promise<{ emails: EmailLog[]; total: number }> {
    const offset = (page - 1) * limit
    const [rows, count] = await Promise.all([
      this.pool.query<EmailLog>(
        'SELECT * FROM email_logs WHERE workspace_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
        [workspaceId, limit, offset]
      ),
      this.pool.query<{ count: string }>(
        'SELECT COUNT(*) FROM email_logs WHERE workspace_id = $1',
        [workspaceId]
      )
    ])
    return { emails: rows.rows, total: parseInt(count.rows[0].count) }
  }

  async listInbound(workspaceId: string, page = 1, limit = 20): Promise<{ logs: unknown[]; total: number }> {
    const offset = (page - 1) * limit
    const [rows, count] = await Promise.all([
      this.pool.query(
        'SELECT * FROM incoming_email_logs WHERE workspace_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3',
        [workspaceId, limit, offset]
      ),
      this.pool.query<{ count: string }>(
        'SELECT COUNT(*) FROM incoming_email_logs WHERE workspace_id = $1',
        [workspaceId]
      )
    ])
    return { logs: rows.rows, total: parseInt(count.rows[0].count) }
  }

  async getStats(workspaceId: string): Promise<{ total: number; sent: number; failed: number; queued: number; today: number }> {
    const result = await this.pool.query(
      `SELECT status, COUNT(*) as count 
       FROM email_logs 
       WHERE workspace_id = $1 
       GROUP BY status`,
      [workspaceId]
    )
    
    const todayResult = await this.pool.query(
      `SELECT COUNT(*) as count 
       FROM email_logs 
       WHERE workspace_id = $1 
         AND status = 'sent' 
         AND sent_at >= CURRENT_DATE`,
      [workspaceId]
    )

    let sent = 0, failed = 0, queued = 0, total = 0
    for (const row of result.rows) {
      const count = parseInt(row.count)
      total += count
      if (row.status === 'sent') sent = count
      else if (row.status === 'failed') failed = count
      else if (row.status === 'queued') queued = count
    }

    return {
      total,
      sent,
      failed,
      queued,
      today: parseInt(todayResult.rows[0].count)
    }
  }

  async getById(emailId: string, workspaceId: string): Promise<EmailLog> {
    const result = await this.pool.query<EmailLog>(
      'SELECT * FROM email_logs WHERE email_id = $1 AND workspace_id = $2',
      [emailId, workspaceId]
    )
    if (!result.rows[0]) throw new NotFoundError('Email log not found')
    return result.rows[0]
  }

  private async publishWebhookEvent(
    event: 'email.sent' | 'email.failed',
    emailLog: EmailLog
  ): Promise<void> {
    try {
      const redis = getRedisClient()
      await redis.publish('webhook:events', JSON.stringify({
        event,
        workspace_id: emailLog.workspace_id,
        email_id: emailLog.email_id,
        to_email: emailLog.to_email,
        subject: emailLog.subject,
        sent_at: emailLog.sent_at,
        provider_message_id: emailLog.provider_message_id
      }))
    } catch (err) {
      // Non-fatal: webhook publish failure should not affect email delivery
      logger.warn({ err }, 'Failed to publish webhook event')
    }
  }

  async processJob(job: EmailJob): Promise<void> {
    try {
      const credResult = await this.pool.query<{
        encrypted_value: string; encryption_key_id: string; provider_type: string
      }>(
        'SELECT encrypted_value, encryption_key_id, provider_type FROM credentials WHERE credential_id = $1',
        [job.credentialId]
      )
      const cred = credResult.rows[0]
      if (!cred) throw new NotFoundError('Credential not found for job')

      const plaintext = decrypt(cred.encrypted_value, this.config.credentialMasterKey, cred.encryption_key_id)
      const credData = JSON.parse(plaintext) as Record<string, unknown>

      const attachments = []
      for (const att of job.attachments ?? []) {
        const resp = await axios.get<ArrayBuffer>(att.url, { responseType: 'arraybuffer' })
        const ext = att.filename.split('.').pop() ?? 'bin'
        const mimeMap: Record<string, string> = {
          pdf: 'application/pdf',
          docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        }
        attachments.push({
          filename: att.filename,
          content: Buffer.from(resp.data),
          contentType: mimeMap[ext] ?? 'application/octet-stream'
        })
      }

      let provider
      if (cred.provider_type === 'gmail') {
        provider = new GmailProvider(
          this.config.gmailClientId,
          this.config.gmailClientSecret,
          this.config.gmailRedirectUri,
          credData as { access_token: string; refresh_token?: string }
        )
      } else if (cred.provider_type === 'outlook') {
        provider = new OutlookProvider(
          job.credentialId,
          cred.encrypted_value,
          cred.encryption_key_id,
          {
            clientId: this.config.outlookClientId,
            clientSecret: this.config.outlookClientSecret,
            tenantId: this.config.outlookTenantId,
            masterKey: this.config.credentialMasterKey
          },
          this.pool
        )
      } else {
        provider = new SmtpProvider(
          credData as { host: string; port: number; secure: boolean; user: string; pass: string }
        )
      }

      const result = await provider.send({
        to: job.to, from: job.from, subject: job.subject, html: job.html, attachments
      })

      await this.pool.query(
        `UPDATE email_logs SET status = 'sent', provider_message_id = $1, sent_at = NOW() WHERE email_id = $2`,
        [result.messageId, job.emailLogId]
      )

      const updatedLog = await this.pool.query<EmailLog>(
        'SELECT * FROM email_logs WHERE email_id = $1',
        [job.emailLogId]
      )
      await this.publishWebhookEvent('email.sent', updatedLog.rows[0])

      logger.info({ emailLogId: job.emailLogId, messageId: result.messageId }, 'Email sent')
    } catch (err) {
      const retryResult = await this.pool.query<{ retry_count: number }>(
        'UPDATE email_logs SET retry_count = retry_count + 1 WHERE email_id = $1 RETURNING retry_count',
        [job.emailLogId]
      )
      const retries = retryResult.rows[0]?.retry_count ?? MAX_RETRIES

      if (retries < MAX_RETRIES) {
        await enqueue(job)
        logger.warn({ emailLogId: job.emailLogId, retries }, 'Email job requeued')
      } else {
        await this.pool.query(
          `UPDATE email_logs SET status = 'failed' WHERE email_id = $1`,
          [job.emailLogId]
        )
        const failedLog = await this.pool.query<EmailLog>(
          'SELECT * FROM email_logs WHERE email_id = $1',
          [job.emailLogId]
        )
        await this.publishWebhookEvent('email.failed', failedLog.rows[0])
        logger.error({ emailLogId: job.emailLogId, err }, 'Email job failed permanently')
      }
    }
  }

  startWorker(): void {
    const loop = async () => {
      while (true) {
        try {
          const job = await dequeue(5)
          if (job) await this.processJob(job)
        } catch (err) {
          logger.error({ err }, 'Worker loop error')
        }
      }
    }
    loop().catch(err => logger.fatal({ err }, 'Worker loop crashed'))
    logger.info('Email worker started')
  }
}
