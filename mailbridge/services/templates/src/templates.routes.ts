import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { TemplatesService, CreateTemplateInput } from './templates.service'
import { authenticate, requireRole, ValidationError, requireScope } from '@mail-bridge/shared'

export function createTemplatesRouter(pool: Pool): Router {
  const router = Router()
  const service = new TemplatesService(pool)

  router.post('/', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { name, subject, html } = req.body as CreateTemplateInput
      if (!name || !subject || !html) throw new ValidationError('name, subject, html are required', 'INVALID_PAYLOAD')
      const template = await service.create(req.body as CreateTemplateInput, req.user!.workspace_id, req.user!.user_id)
      res.status(201).json({ success: true, template })
    } catch (err) { next(err) }
  })

  router.get('/', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const templates = await service.list(req.user!.workspace_id)
      res.json({ success: true, templates })
    } catch (err) { next(err) }
  })

  router.put('/:id', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const template = await service.update(
        req.params.id, req.user!.workspace_id,
        req.body as Partial<CreateTemplateInput>, req.user!.user_id
      )
      res.json({ success: true, template })
    } catch (err) { next(err) }
  })

  router.get('/:id/versions', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const page = parseInt(req.query.page as string ?? '1')
      const limit = parseInt(req.query.limit as string ?? '20')
      const result = await service.getVersions(req.params.id, req.user!.workspace_id, page, limit)
      res.json({ success: true, ...result, page, limit })
    } catch (err) { next(err) }
  })

  router.post('/:id/rollback', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { version } = req.body as { version?: number }
      if (!version) throw new ValidationError('version is required', 'INVALID_PAYLOAD')
      const template = await service.rollback(req.params.id, version, req.user!.workspace_id, req.user!.user_id)
      res.json({ success: true, template })
    } catch (err) { next(err) }
  })

  router.delete('/:id', authenticate, requireScope('templates'), requireRole('member'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.remove(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  return router
}
