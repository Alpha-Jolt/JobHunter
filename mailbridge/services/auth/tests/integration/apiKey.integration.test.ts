import { Pool } from 'pg'
import { ApiKeyService } from '../../src/apiKey.service'
import { getSharedConfig } from '@mail-bridge/shared'

describe('ApiKeyService Integration', () => {
  let pool: Pool
  let service: ApiKeyService
  let workspaceId: string
  let userId: string

  beforeAll(async () => {
    const config = getSharedConfig()
    pool = new Pool({ connectionString: config.databaseUrl })
    service = new ApiKeyService(pool)

    // Setup basic test data
    const wsResult = await pool.query('INSERT INTO workspaces (name) VALUES ($1) RETURNING workspace_id', ['Integration Test WS'])
    workspaceId = wsResult.rows[0].workspace_id

    const userResult = await pool.query(
      'INSERT INTO users (workspace_id, email, password_hash) VALUES ($1, $2, $3) RETURNING user_id',
      [workspaceId, 'test@integration.com', 'hash']
    )
    userId = userResult.rows[0].user_id
  })

  afterAll(async () => {
    await pool.query('DELETE FROM users WHERE user_id = $1', [userId])
    await pool.query('DELETE FROM workspaces WHERE workspace_id = $1', [workspaceId])
    await pool.end()
  })

  it('performs full create -> list -> revoke cycle', async () => {
    // 1. Create
    const key = await service.create({
      workspaceId,
      userId,
      name: 'Integration Key',
      scopes: ['send', 'read']
    })
    
    expect(key.api_key_id).toBeDefined()
    expect(key.raw_key).toBeDefined()
    expect(key.scopes).toEqual(['send', 'read'])

    // 2. List
    const keys = await service.list(workspaceId)
    expect(keys.length).toBeGreaterThan(0)
    
    const listedKey = keys.find(k => k.api_key_id === key.api_key_id)
    expect(listedKey).toBeDefined()
    expect(listedKey!.revoked_at).toBeNull()

    // 3. Revoke
    await service.revoke(key.api_key_id, workspaceId)
    
    const revokedKey = await service.getById(key.api_key_id, workspaceId)
    expect(revokedKey!.revoked_at).not.toBeNull()
  })
})
