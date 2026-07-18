import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { CredentialsService, SmtpInput } from './credentials.service'
import { authenticate, requireRole, ValidationError, logger, requireScope } from '@mail-bridge/shared'
import { CredentialsConfig } from './config'

export function createCredentialsRouter(pool: Pool, config: CredentialsConfig): Router {
  const router = Router()
  const service = new CredentialsService(pool, config)

  router.get('/gmail/connect', authenticate, requireScope('credentials'), requireRole('owner'), (req: Request, res: Response, next: NextFunction) => {
    try {
      res.json({ success: true, url: service.getGmailAuthUrl(req.user!.workspace_id) })
    } catch (err) { next(err) }
  })

  router.get('/gmail/callback', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { code, state } = req.query as { code?: string; state?: string }
      if (!code) throw new ValidationError('Missing OAuth code', 'MISSING_CODE')
      // state carries workspace_id set during connect
      const workspaceId = state ?? ''
      await service.handleGmailCallback(code, workspaceId)
      res.redirect(process.env.FRONTEND_URL ? `${process.env.FRONTEND_URL}/credentials` : 'http://localhost:3000/credentials')
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      logger.error({ err }, 'Gmail OAuth callback failed')
      res.redirect(process.env.FRONTEND_URL ? `${process.env.FRONTEND_URL}/credentials?error=${encodeURIComponent(errorMsg)}` : `http://localhost:3000/credentials?error=${encodeURIComponent(errorMsg)}`)
    }
  })

  router.get('/outlook/connect', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const url = await service.getOutlookAuthUrl(req.user!.workspace_id)
      res.json({ success: true, url })
    } catch (err) { next(err) }
  })

  router.get('/outlook/callback', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { code, state } = req.query as { code?: string; state?: string }
      if (!code) throw new ValidationError('Missing OAuth code', 'MISSING_CODE')
      const workspaceId = state ?? ''
      await service.handleOutlookCallback(code, workspaceId)
      res.redirect(process.env.FRONTEND_URL ? `${process.env.FRONTEND_URL}/credentials` : 'http://localhost:3000/credentials')
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      logger.error({ err }, 'Outlook OAuth callback failed')
      res.redirect(process.env.FRONTEND_URL ? `${process.env.FRONTEND_URL}/credentials?error=${encodeURIComponent(errorMsg)}` : `http://localhost:3000/credentials?error=${encodeURIComponent(errorMsg)}`)
    }
  })

  router.post('/smtp', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { from_email, host, port, user, pass } = req.body as SmtpInput
      if (!from_email || !host || !port || !user || !pass) {
        throw new ValidationError('from_email, host, port, user, pass are required', 'INVALID_PAYLOAD')
      }
      const credential = await service.addSmtp(req.body as SmtpInput, req.user!.workspace_id)
      res.status(201).json({ success: true, ...credential })
    } catch (err) { next(err) }
  })

  router.get('/', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const credentials = await service.list(req.user!.workspace_id)
      res.json({ success: true, credentials })
    } catch (err) { next(err) }
  })

  router.delete('/:id', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.remove(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  router.post('/:id/watch', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.registerGmailWatch(req.params.id, req.user!.workspace_id)
      res.json({ success: true, message: 'Gmail watch registered — push notifications active' })
    } catch (err) { next(err) }
  })

  router.post('/:id/test', authenticate, requireScope('credentials'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Verify credential is accessible (decryptable) — actual send test done by emails service
      await service.getDecrypted(req.params.id, req.user!.workspace_id)
      res.json({ success: true, message: 'Credential is valid and accessible' })
    } catch (err) { next(err) }
  })

  return router
}
