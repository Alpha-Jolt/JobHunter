import express from 'express'
import request from 'supertest'
import { createHealthRouter } from '../../src/health.routes'
import { Pool } from 'pg'
import Redis from 'ioredis'

const mockQuery = jest.fn()
const mockPing = jest.fn()
const mockPool = { query: mockQuery } as unknown as Pool
const mockRedis = { ping: mockPing } as unknown as Redis

const app = express()
app.use('/', createHealthRouter(mockPool, mockRedis))

beforeEach(() => { mockQuery.mockReset(); mockPing.mockReset() })

describe('Health routes', () => {
  it('GET / returns 200 with status ok', async () => {
    const res = await request(app).get('/')
    expect(res.status).toBe(200)
    expect(res.body.status).toBe('ok')
  })

  it('GET /ready returns 200 when DB and Redis ok', async () => {
    mockQuery.mockResolvedValueOnce({ rows: [{ '?column?': 1 }] })
    mockPing.mockResolvedValueOnce('PONG')
    const res = await request(app).get('/ready')
    expect(res.status).toBe(200)
    expect(res.body).toMatchObject({ status: 'ready', db: 'ok', redis: 'ok' })
  })

  it('GET /ready returns 503 when DB is down', async () => {
    mockQuery.mockRejectedValueOnce(new Error('connection refused'))
    mockPing.mockResolvedValueOnce('PONG')
    const res = await request(app).get('/ready')
    expect(res.status).toBe(503)
    expect(res.body).toMatchObject({ status: 'not_ready', db: 'down' })
  })
})
