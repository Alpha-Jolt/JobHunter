import { Pool, PoolClient } from 'pg'
import { TemplatesService } from '../../src/templates.service'

const mockQuery = jest.fn()
const mockRelease = jest.fn()
const mockConnect = jest.fn()

const mockPool = {
  query: mockQuery,
  connect: mockConnect
} as unknown as Pool

const mockClient = {
  query: jest.fn(),
  release: mockRelease
} as unknown as PoolClient

beforeEach(() => {
  mockQuery.mockReset()
  mockConnect.mockReset()
  mockRelease.mockReset()
  ;(mockClient.query as jest.Mock).mockReset()
  mockConnect.mockResolvedValue(mockClient)
})

const service = new TemplatesService(mockPool)
const WS = 'ws-1'
const USER = 'user-1'
const TMPL_ID = 'tmpl-1'

const baseTemplate = {
  template_id: TMPL_ID, workspace_id: WS, name: 'T1',
  subject: 'Hi {{name}}', html: '<p>{{name}}</p>',
  variables: ['name'], validation_rules: {}, version: 1,
  created_by: USER, created_at: new Date(), updated_at: new Date()
}

describe('TemplatesService', () => {
  describe('create', () => {
    it('inserts template and returns with version=1', async () => {
      mockQuery.mockResolvedValueOnce({ rows: [baseTemplate] })
      const result = await service.create({ name: 'T1', subject: 'Hi', html: '<p/>' }, WS, USER)
      expect(result.version).toBe(1)
      expect(result.template_id).toBe(TMPL_ID)
    })
  })

  describe('list', () => {
    it('returns workspace templates', async () => {
      mockQuery.mockResolvedValueOnce({ rows: [baseTemplate] })
      const result = await service.list(WS)
      expect(result).toHaveLength(1)
    })
  })

  describe('update', () => {
    it('snapshots previous version and increments version', async () => {
      const clientQuery = mockClient.query as jest.Mock
      clientQuery.mockResolvedValueOnce(undefined)                          // BEGIN
      clientQuery.mockResolvedValueOnce({ rows: [baseTemplate] })           // SELECT current
      clientQuery.mockResolvedValueOnce({ rows: [] })                       // INSERT snapshot
      clientQuery.mockResolvedValueOnce({ rows: [{ ...baseTemplate, version: 2 }] }) // UPDATE
      clientQuery.mockResolvedValueOnce(undefined)                          // COMMIT

      const result = await service.update(TMPL_ID, WS, { name: 'T2' }, USER)
      expect(result.version).toBe(2)
    })

    it('throws NotFoundError for unknown template', async () => {
      const clientQuery = mockClient.query as jest.Mock
      clientQuery.mockResolvedValueOnce(undefined)          // BEGIN
      clientQuery.mockResolvedValueOnce({ rows: [] })       // SELECT — not found
      clientQuery.mockResolvedValueOnce(undefined)          // ROLLBACK

      await expect(service.update('bad-id', WS, { name: 'X' }, USER))
        .rejects.toMatchObject({ statusCode: 404 })
    })
  })

  describe('getVersions', () => {
    it('returns paginated version history', async () => {
      mockQuery.mockResolvedValueOnce({ rows: [{ template_id: TMPL_ID }] }) // ownership check
      mockQuery.mockResolvedValueOnce({ rows: [{ version_id: 'v1', version: 1 }] }) // versions
      mockQuery.mockResolvedValueOnce({ rows: [{ count: '1' }] })           // count
      const result = await service.getVersions(TMPL_ID, WS)
      expect(result.total).toBe(1)
      expect(result.versions).toHaveLength(1)
    })
  })

  describe('rollback', () => {
    it('restores fields and sets version to max+1', async () => {
      const clientQuery = mockClient.query as jest.Mock
      clientQuery.mockResolvedValueOnce(undefined)                          // BEGIN
      clientQuery.mockResolvedValueOnce({ rows: [{ version_id: 'v1', version: 1, name: 'Old', subject: 'S', html: '<p/>', variables: [], validation_rules: {} }] }) // snapshot
      clientQuery.mockResolvedValueOnce({ rows: [baseTemplate] })           // current
      clientQuery.mockResolvedValueOnce({ rows: [] })                       // snapshot current
      clientQuery.mockResolvedValueOnce({ rows: [{ ...baseTemplate, version: 2, name: 'Old' }] }) // UPDATE
      clientQuery.mockResolvedValueOnce(undefined)                          // COMMIT

      const result = await service.rollback(TMPL_ID, 1, WS, USER)
      expect(result.version).toBe(2)
    })

    it('throws NotFoundError for unknown version', async () => {
      const clientQuery = mockClient.query as jest.Mock
      clientQuery.mockResolvedValueOnce(undefined)    // BEGIN
      clientQuery.mockResolvedValueOnce({ rows: [] }) // snapshot not found
      clientQuery.mockResolvedValueOnce(undefined)    // ROLLBACK

      await expect(service.rollback(TMPL_ID, 99, WS, USER))
        .rejects.toMatchObject({ statusCode: 404 })
    })
  })
})
