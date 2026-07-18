import { Request, Response, NextFunction } from 'express'
import jwt from 'jsonwebtoken'
import { getSharedConfig } from '../../config'
import { AuthenticationError } from '../error-handling'
import { AuthUser } from '../../models/types'
import { getRedisClient } from '../../queue/emailQueue'
import { authenticateApiKey } from './apiKey.middleware'

export async function authenticate(
  req: Request,
  _res: Response,
  next: NextFunction
): Promise<void> {
  try {
    const header = req.headers.authorization
    if (!header?.startsWith('Bearer ')) {
      throw new AuthenticationError('Missing or invalid Authorization header', 'MISSING_TOKEN')
    }

    const token = header.slice(7)

    if (token.startsWith('sk_') || token.startsWith('sk_test_')) {
      return await authenticateApiKey(token, req, next)
    }

    const config = getSharedConfig()

    // Check token blocklist (logout)
    const blocked = await getRedisClient().get(`blocklist:${token}`)
    if (blocked) throw new AuthenticationError('Token has been revoked', 'TOKEN_REVOKED')

    const payload = jwt.verify(token, config.jwtSecret) as AuthUser & { iat: number; exp: number }
    req.user = {
      user_id: payload.user_id,
      workspace_id: payload.workspace_id,
      tier: payload.tier,
      role: payload.role
    }
    next()
  } catch (err) {
    if (err instanceof AuthenticationError) return next(err)
    next(new AuthenticationError('Invalid or expired token', 'INVALID_TOKEN'))
  }
}
