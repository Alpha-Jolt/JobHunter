import axios from 'axios'
import { Pool } from 'pg'
import { Redis } from 'ioredis'
import { logger } from '@mail-bridge/shared'
import { WebhookEvent, WebhookDelivery } from '@mail-bridge/shared'
import { WebhooksService } from './webhooks.service'

interface WebhookEventPayload {
  event: WebhookEvent
  workspace_id: string
  email_id: string
  to_email: string
  subject: string
  sent_at: string | null
  provider_message_id: string | null
}

const MAX_ATTEMPTS = 5

/**
 * Attempt delivery to a single webhook URL.
 * Updates delivery record on success or failure.
 */
export async function attemptDelivery(
  delivery: WebhookDelivery,
  webhookUrl: string,
  secret: string,
  pool: Pool
): Promise<void> {
  const payloadStr = JSON.stringify(delivery.payload)
  const signature = WebhooksService.buildSignature(secret, payloadStr)

  try {
    await axios.post(webhookUrl, delivery.payload, {
      headers: {
        'Content-Type': 'application/json',
        'X-Mail-Bridge-Signature': signature,
        'X-Mail-Bridge-Event': delivery.event
      },
      timeout: 10_000
    })

    await pool.query(
      `UPDATE webhook_deliveries SET status = 'delivered', delivered_at = NOW(), attempts = attempts + 1
       WHERE delivery_id = $1`,
      [delivery.delivery_id]
    )
    logger.info({ deliveryId: delivery.delivery_id, event: delivery.event }, 'Webhook delivered')
  } catch (err) {
    const newAttempts = delivery.attempts + 1
    const lastError = err instanceof Error ? err.message : String(err)

    if (newAttempts >= MAX_ATTEMPTS) {
      await pool.query(
        `UPDATE webhook_deliveries SET status = 'failed', attempts = $1, last_error = $2
         WHERE delivery_id = $3`,
        [newAttempts, lastError, delivery.delivery_id]
      )
      logger.warn({ deliveryId: delivery.delivery_id, attempts: newAttempts }, 'Webhook delivery failed permanently')
    } else {
      // Exponential backoff: 30s * 2^attempts
      const backoffSeconds = 30 * Math.pow(2, newAttempts)
      await pool.query(
        `UPDATE webhook_deliveries SET attempts = $1, last_error = $2,
           next_retry_at = NOW() + ($3 || ' seconds')::interval
         WHERE delivery_id = $4`,
        [newAttempts, lastError, backoffSeconds, delivery.delivery_id]
      )
      logger.warn({ deliveryId: delivery.delivery_id, attempts: newAttempts, backoffSeconds }, 'Webhook delivery failed, will retry')
    }
  }
}

/**
 * Dispatch event to all matching active webhooks for the workspace.
 */
async function dispatchToWorkspaceWebhooks(
  payload: WebhookEventPayload,
  service: WebhooksService,
  pool: Pool
): Promise<void> {
  const { rows: webhooks } = await pool.query<{
    webhook_id: string; url: string; secret_hash: string
  }>(
    `SELECT webhook_id, url, secret_hash FROM webhooks
     WHERE workspace_id = $1 AND is_active = TRUE AND events @> $2::jsonb`,
    [payload.workspace_id, JSON.stringify([payload.event])]
  )

  for (const webhook of webhooks) {
    const deliveryResult = await pool.query<WebhookDelivery>(
      `INSERT INTO webhook_deliveries (webhook_id, email_id, event, payload, next_retry_at)
       VALUES ($1, $2, $3, $4, NULL) RETURNING *`,
      [webhook.webhook_id, payload.email_id, payload.event, JSON.stringify(payload)]
    )
    const delivery = deliveryResult.rows[0]
    const secret = service.decryptSecret(webhook.secret_hash)
    await attemptDelivery(delivery, webhook.url, secret, pool)
  }
}

/**
 * Subscribe to Redis webhook:events channel and dispatch deliveries.
 */
export function startWebhookSubscriber(
  subscriber: Redis,
  service: WebhooksService,
  pool: Pool
): void {
  subscriber.subscribe('webhook:events', (err) => {
    if (err) logger.error({ err }, 'Failed to subscribe to webhook:events')
    else logger.info('Webhook subscriber listening on webhook:events')
  })

  subscriber.on('message', (_channel: string, message: string) => {
    let payload: WebhookEventPayload
    try {
      payload = JSON.parse(message) as WebhookEventPayload
    } catch {
      logger.warn({ message }, 'Invalid webhook event payload')
      return
    }
    dispatchToWorkspaceWebhooks(payload, service, pool).catch(err =>
      logger.error({ err }, 'Webhook dispatch error')
    )
  })
}

/**
 * Retry loop: picks up pending deliveries past next_retry_at.
 * Uses SELECT FOR UPDATE SKIP LOCKED for multi-instance safety.
 */
export function startRetryLoop(service: WebhooksService, pool: Pool): void {
  setInterval(async () => {
    const client = await pool.connect()
    try {
      await client.query('BEGIN')

      const { rows: pending } = await client.query<WebhookDelivery & { url: string; secret_hash: string }>(
        `SELECT wd.*, w.url, w.secret_hash
         FROM webhook_deliveries wd
         JOIN webhooks w ON w.webhook_id = wd.webhook_id
         WHERE wd.status = 'pending' AND wd.next_retry_at <= NOW()
         FOR UPDATE OF wd SKIP LOCKED
         LIMIT 20`
      )

      await client.query('COMMIT')

      for (const row of pending) {
        const secret = service.decryptSecret(row.secret_hash)
        await attemptDelivery(row, row.url, secret, pool)
      }
    } catch (err) {
      await client.query('ROLLBACK')
      logger.error({ err }, 'Webhook retry loop error')
    } finally {
      client.release()
    }
  }, 30_000)

  logger.info('Webhook retry loop started (30s interval)')
}
