import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { AdminService } from './admin.service'
import { authenticate, requireRole, ValidationError, requireScope } from '@mail-bridge/shared'
import { FlatRole } from '@mail-bridge/shared'

export function createAdminRouter(pool: Pool): Router {
  const router = Router()
  const service = new AdminService(pool)

  router.get('/users', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const users = await service.listUsers(req.user!.workspace_id)
      res.json({ success: true, users })
    } catch (err) { next(err) }
  })

  router.post('/users', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, role } = req.body as { email?: string; role?: FlatRole }
      if (!email || !role) throw new ValidationError('email and role are required', 'INVALID_PAYLOAD')
      const user = await service.inviteUser(email, role, req.user!.workspace_id)
      res.status(201).json({ success: true, user })
    } catch (err) { next(err) }
  })

  router.put('/users/:id/role', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { role } = req.body as { role?: FlatRole }
      if (!role) throw new ValidationError('role is required', 'INVALID_PAYLOAD')
      await service.changeRole(req.params.id, role, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  router.delete('/users/:id', authenticate, requireScope('admin'), requireRole('owner'), async (req: Request, res: Response, next: NextFunction) => {
    try {
      await service.removeUser(req.params.id, req.user!.workspace_id)
      res.json({ success: true })
    } catch (err) { next(err) }
  })

  return router
}
