import { Pool } from 'pg'
import { ApiKeyService } from '../../src/apiKey.service'
import { createHash } from 'crypto'

function mockPool(queryResults: Record<string, Array<Record<string, unknown>>>): Pool {
  return {
    query: jest.fn().mockImplementation((sql: string, params: unknown[]) => {
      if (sql.includes('INSERT INTO api_keys')) {
        return Promise.resolve({ rows: [{ api_key_id: 'test-id', name: params[2], scopes: JSON.parse(params[4] as string), created_at: new Date() }] })
      }
      if (sql.includes('SELECT api_key_id')) {
        if (sql.includes('ORDER BY created_at DESC')) {
            return Promise.resolve({ rows: queryResults['list'] ?? [] })
        }
        return Promise.resolve({ rows: queryResults['getById'] ?? [] })
      }
      if (sql.includes('UPDATE api_keys')) {
        return Promise.resolve({ rows: [] })
      }
      return Promise.resolve({ rows: [] })
    })
  } as unknown as Pool
}

describe('ApiKeyService', () => {
  const originalEnv = process.env

  beforeEach(() => {
    jest.resetModules()
    process.env = { ...originalEnv }
  })

  afterAll(() => {
    process.env = originalEnv
  })

  describe('create', () => {
    it('generates a key with sk_ prefix in production', async () => {
      process.env.NODE_ENV = 'production'
      const pool = mockPool({})
      const service = new ApiKeyService(pool)
      
      const result = await service.create({
        workspaceId: 'ws-1',
        userId: 'u-1',
        name: 'Prod Key'
      })

      expect(result.raw_key.startsWith('sk_')).toBe(true)
      expect(result.raw_key.startsWith('sk_test_')).toBe(false)
      expect(result.raw_key.length).toBeGreaterThan(40)
      
      const calls = (pool.query as jest.Mock).mock.calls
      expect(calls[0][1][1]).toEqual(createHash('sha256').update(result.raw_key).digest('hex'))
    })

    it('generates a key with sk_test_ prefix outside production', async () => {
      process.env.NODE_ENV = 'development'
      const pool = mockPool({})
      const service = new ApiKeyService(pool)
      
      const result = await service.create({
        workspaceId: 'ws-1',
        userId: 'u-1',
        name: 'Test Key'
      })

      expect(result.raw_key.startsWith('sk_test_')).toBe(true)
    })

    it('defaults to send scope', async () => {
      const pool = mockPool({})
      const service = new ApiKeyService(pool)
      
      await service.create({ workspaceId: 'ws-1', userId: 'u-1', name: 'Key' })
      const calls = (pool.query as jest.Mock).mock.calls
      expect(calls[0][1][4]).toBe('["send"]')
    })
  })

  describe('list', () => {
    it('returns keys without key_hash', async () => {
      const mockRows = [{
        api_key_id: '1',
        workspace_id: 'ws-1',
        name: 'Key',
        created_by: 'u-1',
        scopes: ['send'],
        last_used_at: null,
        expires_at: null,
        revoked_at: null,
        created_at: new Date(),
        updated_at: new Date()
      }]
      
      const pool = mockPool({ list: mockRows })
      const service = new ApiKeyService(pool)
      
      const result = await service.list('ws-1')
      expect(result).toHaveLength(1)
      expect(result[0]).not.toHaveProperty('key_hash')
      expect(result[0].name).toBe('Key')
    })
  })

  describe('revoke', () => {
    it('updates revoked_at', async () => {
      const pool = mockPool({})
      const service = new ApiKeyService(pool)
      
      await service.revoke('key-1', 'ws-1')
      const calls = (pool.query as jest.Mock).mock.calls
      expect(calls[0][0]).toContain('SET revoked_at = NOW()')
      expect(calls[0][1]).toEqual(['key-1', 'ws-1'])
    })
  })
})
