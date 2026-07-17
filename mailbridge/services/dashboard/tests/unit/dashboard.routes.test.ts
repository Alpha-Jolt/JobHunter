import express from 'express'
import request from 'supertest'
import jwt from 'jsonwebtoken'
import { createDashboardRouter } from '../../src/dashboard.routes'
import { Pool } from 'pg'

process.env.JWT_SECRET = 'test-secret-32-chars-minimum-here!!'
process.env.REDIS_URL = 'redis://localhost:6379/1'

const mockQuery = jest.fn()
const mockPool = { query: mockQuery } as unknown as Pool

// Mock Redis blocklist check (no blocked tokens in tests)
jest.mock('ioredis', () => {
  return jest.fn().mockImplementation(() => ({
    get: jest.fn().mockResolvedValue(null),
    set: jest.fn(),
    setex: jest.fn(),
    on: jest.fn(),
    subscribe: jest.fn(),
    publish: jest.fn()
  }))
})

const app = express()
app.use(express.json())
app.use('/', createDashboardRouter(mockPool))

const validToken = jwt.sign(
  { user_id: 'u1', workspace_id: 'ws-1', tier: 'free', role: 'owner' },
  'test-secret-32-chars-minimum-here!!',
  { expiresIn: '1h' }
)

beforeEach(() => mockQuery.mockReset())

describe('Dashboard routes', () => {
  it('GET / returns 401 without token', async () => {
    const res = await request(app).get('/')
    expect(res.status).toBe(401)
  })

  it('GET / returns 200 HTML with valid token', async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ name: 'My Team', tier: 'free' }] })
    mockQuery.mockResolvedValueOnce({ rows: [{ count: '2' }] })
    mockQuery.mockResolvedValueOnce({ rows: [{ count: '5' }] })
    mockQuery.mockResolvedValueOnce({ rows: [] })
    const res = await request(app).get('/').set('Authorization', `Bearer ${validToken}`)
    expect(res.status).toBe(200)
    expect(res.headers['content-type']).toMatch(/html/)
  })

  it('GET / HTML contains workspace name', async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ name: 'Acme Corp', tier: 'pro' }] })
    mockQuery.mockResolvedValueOnce({ rows: [{ count: '1' }] })
    mockQuery.mockResolvedValueOnce({ rows: [{ count: '3' }] })
    mockQuery.mockResolvedValueOnce({ rows: [] })
    const res = await request(app).get('/').set('Authorization', `Bearer ${validToken}`)
    expect(res.text).toContain('Acme Corp')
  })
})
