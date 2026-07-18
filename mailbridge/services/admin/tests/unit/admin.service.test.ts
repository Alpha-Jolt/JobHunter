import { Pool } from 'pg'
import { AdminService } from '../../src/admin.service'

const mockQuery = jest.fn()
const mockPool = { query: mockQuery } as unknown as Pool
const service = new AdminService(mockPool)
const WS = 'ws-1'
const USER = 'user-1'

beforeEach(() => mockQuery.mockReset())

describe('AdminService', () => {
  describe('listUsers', () => {
    it('returns active workspace users', async () => {
      const rows = [{ user_id: 'u1', email: 'a@b.com', role: 'member' }]
      mockQuery.mockResolvedValueOnce({ rows })
      const result = await service.listUsers(WS)
      expect(result).toEqual(rows)
      expect(mockQuery).toHaveBeenCalledWith(expect.stringContaining('deleted_at IS NULL'), [WS])
    })
  })

  describe('inviteUser', () => {
    it('creates user with INVITE_PENDING hash', async () => {
      const user = { user_id: 'u2', email: 'new@b.com', role: 'member' }
      mockQuery.mockResolvedValueOnce({ rows: [] })       // no existing user
      mockQuery.mockResolvedValueOnce({ rows: [user] })   // insert
      const result = await service.inviteUser('new@b.com', 'member', WS)
      expect(result.email).toBe('new@b.com')
    })

    it('throws ConflictError if email already exists', async () => {
      mockQuery.mockResolvedValueOnce({ rows: [{ user_id: 'existing' }] })
      await expect(service.inviteUser('exists@b.com', 'member', WS))
        .rejects.toMatchObject({ code: 'USER_EXISTS' })
    })
  })

  describe('changeRole', () => {
    it('resolves when user found', async () => {
      mockQuery.mockResolvedValueOnce({ rowCount: 1 })
      await expect(service.changeRole(USER, 'owner', WS)).resolves.toBeUndefined()
    })

    it('throws NotFoundError for unknown user', async () => {
      mockQuery.mockResolvedValueOnce({ rowCount: 0 })
      await expect(service.changeRole('unknown', 'owner', WS))
        .rejects.toMatchObject({ statusCode: 404 })
    })
  })

  describe('removeUser', () => {
    it('sets deleted_at on user', async () => {
      mockQuery.mockResolvedValueOnce({ rowCount: 1 })
      await expect(service.removeUser(USER, WS)).resolves.toBeUndefined()
    })

    it('throws NotFoundError for unknown user', async () => {
      mockQuery.mockResolvedValueOnce({ rowCount: 0 })
      await expect(service.removeUser('unknown', WS))
        .rejects.toMatchObject({ statusCode: 404 })
    })
  })
})
