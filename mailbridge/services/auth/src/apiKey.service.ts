import { Pool } from 'pg'
import { randomBytes, createHash } from 'crypto'
import { ApiKey } from '@mail-bridge/shared'

export class ApiKeyService {
  constructor(private readonly pool: Pool) {}

  async create(input: {
    workspaceId: string
    userId: string
    name: string
    scopes?: string[]
    expiresAt?: Date
  }): Promise<{ api_key_id: string; raw_key: string; name: string; scopes: string[]; created_at: Date }> {
    const prefix = process.env.NODE_ENV === 'production' ? 'sk_' : 'sk_test_'
    const random = randomBytes(32).toString('base64url')
    const rawKey = `${prefix}${random}`
    const keyHash = createHash('sha256').update(rawKey).digest('hex')
    const scopesStr = JSON.stringify(input.scopes || ['send'])

    const result = await this.pool.query(
      `INSERT INTO api_keys (workspace_id, key_hash, name, created_by, scopes, expires_at)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING api_key_id, name, scopes, created_at`,
      [input.workspaceId, keyHash, input.name, input.userId, scopesStr, input.expiresAt || null]
    )

    const row = result.rows[0]
    return {
      api_key_id: row.api_key_id,
      raw_key: rawKey,
      name: row.name,
      scopes: row.scopes,
      created_at: row.created_at
    }
  }

  async list(workspaceId: string): Promise<Omit<ApiKey, 'key_hash'>[]> {
    const result = await this.pool.query(
      `SELECT api_key_id, workspace_id, name, created_by, scopes, last_used_at, expires_at, revoked_at, created_at, updated_at
       FROM api_keys
       WHERE workspace_id = $1
       ORDER BY created_at DESC`,
      [workspaceId]
    )
    return result.rows
  }

  async getById(apiKeyId: string, workspaceId: string): Promise<Omit<ApiKey, 'key_hash'> | null> {
    const result = await this.pool.query(
      `SELECT api_key_id, workspace_id, name, created_by, scopes, last_used_at, expires_at, revoked_at, created_at, updated_at
       FROM api_keys
       WHERE api_key_id = $1 AND workspace_id = $2`,
      [apiKeyId, workspaceId]
    )
    return result.rows[0] || null
  }

  async revoke(apiKeyId: string, workspaceId: string): Promise<void> {
    await this.pool.query(
      `UPDATE api_keys
       SET revoked_at = NOW(), updated_at = NOW()
       WHERE api_key_id = $1 AND workspace_id = $2`,
      [apiKeyId, workspaceId]
    )
  }
}
