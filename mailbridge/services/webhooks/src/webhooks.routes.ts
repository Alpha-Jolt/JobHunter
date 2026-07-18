import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { WebhooksService, CreateWebhookInput } from './webhooks.service'
import { authenticate, requireRole, ValidationError, requireScope } from '@mail-bridge/shared'
import { WebhooksConfig } from './config'

export function createWebhooksRouter(pool: Pool, config: WebhooksConfig): Router {
  const router = Router()
  const service = new WebhooksService(pool, config.credentialMasterKey)

  router.post('/', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { url, events, secret } = req.body as CreateWebhookInput
      if (!url || !events?.length || !secret) {
        throw new ValidationError('url, events, secret are required', 'INVALID_PAYLOAD')
      }
      const webhook = await service.create(req.body as CreateWebhookInput, req.user!.workspace_id, req.user!.user_id)
      res.status(201).json({ success: true, webhook_id: webhook.webhook_id, secret: webhook.secret })
    } catch (err) { next(err) }
  })

  router.get('/', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const webhooks = await service.list(req.user!.workspace_id)
      res.json({ success: true, webhooks })
    } catch (err) { next(err) }
  })

  router.put('/:id', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const webhook = await service.update(req.params.id, req.user!.workspace_id, req.body)
      res.json({ success: true, webhook })
    } catch (err) { next(err) }
  })

  router.delete('/:id', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.remove(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  router.get('/:id/deliveries', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const page = parseInt(req.query.page as string ?? '1')
      const limit = parseInt(req.query.limit as string ?? '20')
      const result = await service.getDeliveries(req.params.id, req.user!.workspace_id, page, limit)
      res.json({ success: true, ...result, page, limit })
    } catch (err) { next(err) }
  })

  router.post('/:id/test', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const webhooks = await service.list(req.user!.workspace_id)
      const webhook = webhooks.find(w => w.webhook_id === req.params.id)
      if (!webhook) throw new ValidationError('Webhook not found', 'NOT_FOUND')

      // Get secret_hash from DB for test delivery
      const row = await pool.query<{ secret_hash: string }>(
        'SELECT secret_hash FROM webhooks WHERE webhook_id = $1',
        [req.params.id]
      )
      const secret = service.decryptSecret(row.rows[0].secret_hash)

      const { attemptDelivery } = await import('./webhookDispatcher')
      const testDelivery = await pool.query(
        `INSERT INTO webhook_deliveries (webhook_id, event, payload)
         VALUES ($1, 'email.sent', $2) RETURNING *`,
        [req.params.id, JSON.stringify({ event: 'email.sent', test: true })]
      )
      await attemptDelivery(testDelivery.rows[0], webhook.url, secret, pool)
      res.json({ success: true, delivery_id: testDelivery.rows[0].delivery_id })
    } catch (err) { next(err) }
  })

  return router
}
