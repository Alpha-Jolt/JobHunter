import { Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { WorkspaceTier, FlatRole, EnterpriseRole } from '../../models/types'
import { AuthorizationError } from '../error-handling'

const TIER_LEVELS: Record<WorkspaceTier, number> = { free: 0, pro: 1, enterprise: 2 }
const FLAT_ROLE_LEVELS: Record<FlatRole, number> = { member: 0, owner: 1 }
const ENTERPRISE_ROLE_LEVELS: Record<EnterpriseRole, number> = {
  user: 0, admin: 1, 'operational-admin': 2, 'system-admin': 3
}

export function requireTier(minTier: WorkspaceTier) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    const tier = req.user?.tier as WorkspaceTier
    if (!tier || TIER_LEVELS[tier] < TIER_LEVELS[minTier]) {
      return next(new AuthorizationError(`Requires ${minTier} tier or above`, 'INSUFFICIENT_TIER'))
    }
    next()
  }
}

export function requireRole(minRole: FlatRole | EnterpriseRole, pool?: Pool) {
  return async (req: Request, _res: Response, next: NextFunction): Promise<void> => {
    try {
      const user = req.user
      if (!user) return next(new AuthorizationError('Not authenticated', 'NOT_AUTHENTICATED'))

      if (user.tier === 'enterprise' && pool) {
        // Enterprise: resolve role from workspace_roles table
        const result = await pool.query<{ role: EnterpriseRole }>(
          'SELECT role FROM workspace_roles WHERE workspace_id = $1 AND user_id = $2',
          [user.workspace_id, user.user_id]
        )
        const enterpriseRole = result.rows[0]?.role ?? 'user'
        const required = minRole as EnterpriseRole
        if (ENTERPRISE_ROLE_LEVELS[enterpriseRole] < (ENTERPRISE_ROLE_LEVELS[required] ?? 0)) {
          return next(new AuthorizationError(`Requires ${minRole} role or above`, 'INSUFFICIENT_ROLE'))
        }
      } else {
        // Free/Pro: flat role check
        const flatRole = user.role as FlatRole
        const required = minRole as FlatRole
        if (FLAT_ROLE_LEVELS[flatRole] < (FLAT_ROLE_LEVELS[required] ?? 0)) {
          return next(new AuthorizationError(`Requires ${minRole} role or above`, 'INSUFFICIENT_ROLE'))
        }
      }
      next()
    } catch (err) {
      next(err)
    }
  }
}
