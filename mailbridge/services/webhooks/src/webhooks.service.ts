import { Pool } from 'pg'
import { createHmac, randomBytes } from 'crypto'
import { encryptCredential, decryptCredential, NotFoundError, ValidationError } from '@mail-bridge/shared'
import { Webhook, WebhookDelivery, WebhookEvent } from '@mail-bridge/shared'

export interface CreateWebhookInput {
  url: string
  events: WebhookEvent[]
  secret: string
}

export class WebhooksService {
  constructor(
    private readonly pool: Pool,
    private readonly masterKey: string
  ) {}

  private encryptSecret(secret: string): string {
    const keyId = randomBytes(16).toString('hex')
    // Store as keyId:encryptedValue so we can decrypt later
    const encrypted = encryptCredential(secret, this.masterKey, keyId)
    return `${keyId}:${encrypted}`
  }

  decryptSecret(stored: string): string {
    const colonIdx = stored.indexOf(':')
    const keyId = stored.substring(0, colonIdx)
    const encrypted = stored.substring(colonIdx + 1)
    return decryptCredential(encrypted, this.masterKey, keyId)
  }

  async create(input: CreateWebhookInput, workspaceId: string, userId: string): Promise<Webhook & { secret: string }> {
    if (!input.url || !input.events?.length || !input.secret) {
      throw new ValidationError('url, events, secret are required', 'INVALID_PAYLOAD')
    }

    const secretHash = this.encryptSecret(input.secret)

    const result = await this.pool.query<Webhook>(
      `INSERT INTO webhooks (workspace_id, url, events, secret_hash, created_by)
       VALUES ($1, $2, $3, $4, $5) RETURNING *`,
      [workspaceId, input.url, JSON.stringify(input.events), secretHash, userId]
    )

    // Return raw secret only at creation — never stored in plaintext
    return { ...result.rows[0], secret: input.secret }
  }

  async list(workspaceId: string): Promise<Omit<Webhook, never>[]> {
    const result = await this.pool.query<Webhook>(
      `SELECT webhook_id, workspace_id, url, events, is_active, created_by, created_at
       FROM webhooks WHERE workspace_id = $1 ORDER BY created_at DESC`,
      [workspaceId]
    )
    return result.rows
  }

  async update(
    webhookId: string,
    workspaceId: string,
    input: Partial<Pick<CreateWebhookInput, 'url' | 'events'> & { is_active: boolean }>
  ): Promise<Webhook> {
    const result = await this.pool.query<Webhook>(
      `UPDATE webhooks SET
         url = COALESCE($1, url),
         events = COALESCE($2, events),
         is_active = COALESCE($3, is_active)
       WHERE webhook_id = $4 AND workspace_id = $5
       RETURNING webhook_id, workspace_id, url, events, is_active, created_by, created_at`,
      [
        input.url ?? null,
        input.events ? JSON.stringify(input.events) : null,
        input.is_active ?? null,
        webhookId, workspaceId
      ]
    )
    if (!result.rows[0]) throw new NotFoundError('Webhook not found')
    return result.rows[0]
  }

  async remove(webhookId: string, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      'DELETE FROM webhooks WHERE webhook_id = $1 AND workspace_id = $2',
      [webhookId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('Webhook not found')
  }

  async getDeliveries(
    webhookId: string,
    workspaceId: string,
    page = 1,
    limit = 20
  ): Promise<{ deliveries: WebhookDelivery[]; total: number }> {
    // Verify ownership
    const check = await this.pool.query(
      'SELECT 1 FROM webhooks WHERE webhook_id = $1 AND workspace_id = $2',
      [webhookId, workspaceId]
    )
    if (!check.rows[0]) throw new NotFoundError('Webhook not found')

    const offset = (page - 1) * limit
    const [rows, count] = await Promise.all([
      this.pool.query<WebhookDelivery>(
        `SELECT * FROM webhook_deliveries WHERE webhook_id = $1
         ORDER BY created_at DESC LIMIT $2 OFFSET $3`,
        [webhookId, limit, offset]
      ),
      this.pool.query<{ count: string }>(
        'SELECT COUNT(*) FROM webhook_deliveries WHERE webhook_id = $1',
        [webhookId]
      )
    ])
    return { deliveries: rows.rows, total: parseInt(count.rows[0].count) }
  }

  /** Build HMAC-SHA256 signature for delivery */
  static buildSignature(secret: string, payload: string): string {
    return 'sha256=' + createHmac('sha256', secret).update(payload).digest('hex')
  }
}
