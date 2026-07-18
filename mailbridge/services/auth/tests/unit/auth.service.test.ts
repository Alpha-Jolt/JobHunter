import { Pool } from 'pg'
import argon2 from 'argon2'
import jwt from 'jsonwebtoken'
import { AuthService } from '../../src/auth.service'
import { AuthConfig } from '../../src/config'

const config: AuthConfig = {
  port: 3001,
  nodeEnv: 'test',
  databaseUrl: '',
  redisUrl: '',
  jwtSecret: 'test-secret-32-chars-minimum-here',
  jwtExpiresIn: '1h',
  logLevel: 'error'
}

function mockPool(queryResults: Record<string, Array<Record<string, unknown>>>): Pool {
  const calls: string[] = []
  return {
    query: jest.fn().mockImplementation((sql: string, params: unknown[]) => {
      // Match by keyword in SQL
      if (sql.includes('SELECT user_id FROM users WHERE email')) {
        return Promise.resolve({ rows: queryResults['checkEmail'] ?? [] })
      }
      if (sql.includes('INSERT INTO workspaces')) {
        return Promise.resolve({ rows: [{ workspace_id: 'ws-1' }] })
      }
      if (sql.includes('INSERT INTO users')) {
        return Promise.resolve({ rows: [{ user_id: 'user-1' }] })
      }
      if (sql.includes('SELECT u.user_id')) {
        return Promise.resolve({ rows: queryResults['loginUser'] ?? [] })
      }
      return Promise.resolve({ rows: [] })
    }),
    connect: jest.fn().mockResolvedValue({
      query: jest.fn().mockImplementation((sql: string) => {
        if (sql === 'BEGIN' || sql === 'COMMIT' || sql === 'ROLLBACK') return Promise.resolve({})
        if (sql.includes('INSERT INTO workspaces')) return Promise.resolve({ rows: [{ workspace_id: 'ws-1' }] })
        if (sql.includes('INSERT INTO users')) return Promise.resolve({ rows: [{ user_id: 'user-1' }] })
        return Promise.resolve({ rows: [] })
      }),
      release: jest.fn()
    })
  } as unknown as Pool
}

describe('AuthService', () => {
  describe('register', () => {
    it('returns token and user/workspace ids on success', async () => {
      const pool = mockPool({ checkEmail: [] })
      const service = new AuthService(pool, config)
      const result = await service.register({ email: 'a@b.com', password: 'password123', workspace_name: 'Test' })
      expect(result.user_id).toBe('user-1')
      expect(result.workspace_id).toBe('ws-1')
      expect(result.token).toBeDefined()
      expect(result.expires_at).toBeDefined()
    })

    it('throws ConflictError if email already exists', async () => {
      const pool = mockPool({ checkEmail: [{ user_id: 'existing' }] })
      const service = new AuthService(pool, config)
      await expect(service.register({ email: 'a@b.com', password: 'pass', workspace_name: 'T' }))
        .rejects.toMatchObject({ code: 'EMAIL_EXISTS' })
    })
  })

  describe('login', () => {
    it('throws AuthenticationError for unknown email', async () => {
      const pool = mockPool({ loginUser: [] })
      const service = new AuthService(pool, config)
      await expect(service.login({ email: 'x@y.com', password: 'pass' }))
        .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS' })
    })

    it('throws AuthenticationError for wrong password', async () => {
      const hash = await argon2.hash('correct-password')
      const pool = mockPool({
        loginUser: [{ user_id: 'u1', password_hash: hash, workspace_id: 'ws-1', role: 'owner', tier: 'free' }]
      })
      const service = new AuthService(pool, config)
      await expect(service.login({ email: 'a@b.com', password: 'wrong-password' }))
        .rejects.toMatchObject({ code: 'INVALID_CREDENTIALS' })
    })
  })

  describe('refresh', () => {
    it('returns new token for valid token', async () => {
      const pool = mockPool({})
      const service = new AuthService(pool, config)
      const token = jwt.sign({ user_id: 'u1', workspace_id: 'ws-1', tier: 'free', role: 'owner' }, config.jwtSecret, { expiresIn: '1h' })
      const result = await service.refresh(token)
      expect(result.token).toBeDefined()
    })

    it('throws AuthenticationError for invalid token', async () => {
      const pool = mockPool({})
      const service = new AuthService(pool, config)
      await expect(service.refresh('invalid.token.here'))
        .rejects.toMatchObject({ code: 'INVALID_TOKEN' })
    })
  })
})
