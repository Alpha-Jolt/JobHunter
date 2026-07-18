import { Request, Response, NextFunction } from 'express'
import { createHash } from 'crypto'
import { AuthenticationError } from '../error-handling'
import { getPool } from '../../db/pool'
import { getRedisClient } from '../../queue/emailQueue'
import { AuthUser } from '../../models/types'
import { logger } from '../logging'

async function updateLastUsed(apiKeyId: string): Promise<void> {
  try {
    const redis = getRedisClient()
    const redisKey = `apikey:lastseen:${apiKeyId}`
    const alreadyTracked = await redis.get(redisKey)
    if (alreadyTracked) return

    await redis.setex(redisKey, 60, Date.now().toString())

    await getPool().query(
      'UPDATE api_keys SET last_used_at = NOW() WHERE api_key_id = $1',
      [apiKeyId]
    )
  } catch (err) {
    logger.error({ err, apiKeyId }, 'Failed to update API key last_used_at')
  }
}

export async function authenticateApiKey(rawKey: string, req: Request, next: NextFunction): Promise<void> {
  try {
    const keyHash = createHash('sha256').update(rawKey).digest('hex')

    const result = await getPool().query(
      `SELECT ak.api_key_id, ak.workspace_id, ak.created_by, ak.scopes,
              ak.expires_at, ak.revoked_at,
              u.role,
              w.tier
       FROM api_keys ak
       JOIN users u ON u.user_id = ak.created_by
       JOIN workspaces w ON w.workspace_id = ak.workspace_id
       WHERE ak.key_hash = $1
         AND ak.revoked_at IS NULL
         AND (ak.expires_at IS NULL OR ak.expires_at > NOW())`,
      [keyHash]
    )

    if (result.rowCount === 0) {
      throw new AuthenticationError('Invalid, expired, or revoked API key', 'INVALID_API_KEY')
    }

    const keyData = result.rows[0]

    req.user = {
      user_id: keyData.created_by,
      workspace_id: keyData.workspace_id,
      tier: keyData.tier,
      role: keyData.role
    }
    
    // Default to 'send' if no scopes are stored, although schema defaults to '["send"]'
    req.apiKeyScopes = keyData.scopes || ['send']

    void updateLastUsed(keyData.api_key_id)

    next()
  } catch (err) {
    if (err instanceof AuthenticationError) return next(err)
    next(new AuthenticationError('API Key authentication failed', 'INVALID_API_KEY'))
  }
}
