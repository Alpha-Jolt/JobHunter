import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { EmailsService, SendEmailInput, ScheduleEmailInput } from './emails.service'
import { authenticate, requireRole, requireScope } from '@mail-bridge/shared'
import { EmailsConfig } from './config'

export function createEmailsRouter(pool: Pool, config: EmailsConfig): Router {
  const router = Router()
  const service = new EmailsService(pool, config)
  service.startWorker()

  router.post('/send', authenticate, requireScope('send'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const result = await service.send(req.body as SendEmailInput, req.user!.workspace_id)
      res.status(202).json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.post('/batch', authenticate, requireScope('send'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { emails } = req.body as { emails: SendEmailInput[] }
      const result = await service.sendBatch(emails ?? [], req.user!.workspace_id)
      res.status(202).json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.post('/schedule', authenticate, requireScope('send'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const result = await service.scheduleEmail(
        req.body as ScheduleEmailInput,
        req.user!.workspace_id,
        req.user!.user_id
      )
      res.status(201).json({ success: true, ...result })
    } catch (err) { next(err) }
  })

  router.get('/schedule', authenticate, requireScope('read'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const page = parseInt(req.query.page as string ?? '1')
      const limit = parseInt(req.query.limit as string ?? '20')
      const result = await service.listScheduled(req.user!.workspace_id, page, limit)
      res.json({ success: true, ...result, page, limit })
    } catch (err) { next(err) }
  })

  router.delete('/schedule/:id', authenticate, requireScope('send'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.cancelScheduled(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  router.get('/stats', authenticate, requireScope('read'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const stats = await service.getStats(req.user!.workspace_id)
      res.json({ success: true, stats })
    } catch (err) { next(err) }
  })

  router.get('/inbound', authenticate, requireScope('read'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const page = parseInt(req.query.page as string ?? '1')
      const limit = parseInt(req.query.limit as string ?? '20')
      const result = await service.listInbound(req.user!.workspace_id, page, limit)
      res.json({ success: true, ...result, page, limit })
    } catch (err) { next(err) }
  })

  router.get('/', authenticate, requireScope('read'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const page = parseInt(req.query.page as string ?? '1')
      const limit = parseInt(req.query.limit as string ?? '20')
      const result = await service.list(req.user!.workspace_id, page, limit)
      res.json({ success: true, ...result, page, limit })
    } catch (err) { next(err) }
  })

  router.get('/:id', authenticate, requireScope('read'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const email = await service.getById(req.params.id, req.user!.workspace_id)
      res.json({ success: true, email })
    } catch (err) { next(err) }
  })

  return router
}
