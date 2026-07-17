import { Pool } from 'pg'
import argon2 from 'argon2'
import jwt from 'jsonwebtoken'
import { randomUUID } from 'crypto'
import {
  ConflictError,
  AuthenticationError
} from '@mail-bridge/shared'
import { AuthConfig } from './config'

export interface RegisterInput {
  email: string
  password: string
  workspace_name: string
}

export interface LoginInput {
  email: string
  password: string
}

export class AuthService {
  constructor(
    private readonly pool: Pool,
    private readonly config: AuthConfig
  ) {}

  async register(input: RegisterInput): Promise<{ user_id: string; workspace_id: string; token: string; expires_at: string }> {
    const existing = await this.pool.query('SELECT user_id FROM users WHERE email = $1', [input.email])
    if (existing.rows.length > 0) throw new ConflictError('Email already registered', 'EMAIL_EXISTS')

    const password_hash = await argon2.hash(input.password)

    const client = await this.pool.connect()
    try {
      await client.query('BEGIN')
      const ws = await client.query<{ workspace_id: string }>(
        'INSERT INTO workspaces (name) VALUES ($1) RETURNING workspace_id',
        [input.workspace_name]
      )
      const workspace_id = ws.rows[0].workspace_id
      const user = await client.query<{ user_id: string }>(
        'INSERT INTO users (email, password_hash, workspace_id, role) VALUES ($1, $2, $3, $4) RETURNING user_id',
        [input.email, password_hash, workspace_id, 'owner']
      )
      await client.query('COMMIT')

      const user_id = user.rows[0].user_id
      const { token, expires_at } = this.signToken({ user_id, workspace_id, tier: 'free', role: 'owner', email: input.email })
      return { user_id, workspace_id, token, expires_at }
    } catch (err) {
      await client.query('ROLLBACK')
      throw err
    } finally {
      client.release()
    }
  }

  async login(input: LoginInput): Promise<{ token: string; expires_at: string }> {
    const result = await this.pool.query<{ user_id: string; email: string; password_hash: string; workspace_id: string; role: string; tier: string }>(
      `SELECT u.user_id, u.email, u.password_hash, u.workspace_id, u.role,
              w.tier
       FROM users u
       JOIN workspaces w ON w.workspace_id = u.workspace_id
       WHERE u.email = $1 AND u.deleted_at IS NULL`,
      [input.email]
    )
    const row = result.rows[0]
    if (!row) throw new AuthenticationError('Invalid email or password', 'INVALID_CREDENTIALS')

    const valid = await argon2.verify(row.password_hash, input.password)
    if (!valid) throw new AuthenticationError('Invalid email or password', 'INVALID_CREDENTIALS')

    return this.signToken({
      user_id: row.user_id,
      workspace_id: row.workspace_id,
      tier: row.tier as 'free' | 'pro' | 'enterprise',
      role: row.role as 'owner' | 'member',
      email: row.email
    })
  }

  async logout(token: string, redis: import('ioredis').default): Promise<void> {
    // Decode to get expiry without verifying (token may be valid but we want to blocklist it)
    const decoded = jwt.decode(token) as { exp?: number } | null
    const ttl = decoded?.exp ? decoded.exp - Math.floor(Date.now() / 1000) : 86400
    if (ttl > 0) await redis.setex(`blocklist:${token}`, ttl, '1')
  }

  async refresh(token: string): Promise<{ token: string; expires_at: string }> {
    try {
      const payload = jwt.verify(token, this.config.jwtSecret) as {
        user_id: string; workspace_id: string; tier: string; role: string; email?: string
      }
      return this.signToken({
        user_id: payload.user_id,
        workspace_id: payload.workspace_id,
        tier: payload.tier as 'free' | 'pro' | 'enterprise',
        role: payload.role as 'owner' | 'member',
        email: payload.email
      })
    } catch {
      throw new AuthenticationError('Invalid or expired token', 'INVALID_TOKEN')
    }
  }

  async upgrade(userId: string, workspaceId: string, email: string): Promise<{ token: string; expires_at: string }> {
    await this.pool.query(
      "UPDATE workspaces SET tier = 'pro' WHERE workspace_id = $1",
      [workspaceId]
    )
    return this.signToken({
      user_id: userId,
      workspace_id: workspaceId,
      tier: 'pro',
      role: 'owner',
      email: email
    })
  }

  private signToken(payload: { user_id: string; workspace_id: string; tier: string; role: string; email?: string }): { token: string; expires_at: string } {
    const token = jwt.sign(payload, this.config.jwtSecret, {
      expiresIn: this.config.jwtExpiresIn,
      jwtid: randomUUID()
    } as jwt.SignOptions)
    const decoded = jwt.decode(token) as { exp: number }
    const expires_at = new Date(decoded.exp * 1000).toISOString()
    return { token, expires_at }
  }
}
