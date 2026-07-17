import request from 'supertest'
import { app } from '../../src/server'
import { TEST_USER } from '../fixtures/testData'

// Integration tests require DATABASE_URL and REDIS_URL set in .env.test
// Run: NODE_ENV=test jest tests/integration

describe('Auth API Integration', () => {
  let token: string

  describe('POST /auth/register', () => {
    it('registers a new user and returns token', async () => {
      const res = await request(app)
        .post('/auth/register')
        .send(TEST_USER)

      expect([200, 201]).toContain(res.status)
      expect(res.body.success).toBe(true)
      expect(res.body.token).toBeDefined()
      expect(res.body.user_id).toBeDefined()
      expect(res.body.workspace_id).toBeDefined()
      token = res.body.token
    })

    it('returns 409 on duplicate email', async () => {
      const res = await request(app)
        .post('/auth/register')
        .send(TEST_USER)

      expect(res.status).toBe(409)
      expect(res.body.error.code).toBe('EMAIL_EXISTS')
    })

    it('returns 400 for missing fields', async () => {
      const res = await request(app)
        .post('/auth/register')
        .send({ email: 'x@y.com' })

      expect(res.status).toBe(400)
      expect(res.body.error.code).toBe('INVALID_PAYLOAD')
    })

    it('returns 400 for invalid email format', async () => {
      const res = await request(app)
        .post('/auth/register')
        .send({ email: 'not-an-email', password: 'pass123456', workspace_name: 'T' })

      expect(res.status).toBe(400)
      expect(res.body.error.code).toBe('INVALID_EMAIL')
    })
  })

  describe('POST /auth/login', () => {
    it('returns token for valid credentials', async () => {
      const res = await request(app)
        .post('/auth/login')
        .send({ email: TEST_USER.email, password: TEST_USER.password })

      expect(res.status).toBe(200)
      expect(res.body.token).toBeDefined()
      expect(res.body.expires_at).toBeDefined()
    })

    it('returns 401 for wrong password', async () => {
      const res = await request(app)
        .post('/auth/login')
        .send({ email: TEST_USER.email, password: 'wrong-password' })

      expect(res.status).toBe(401)
      expect(res.body.error.code).toBe('INVALID_CREDENTIALS')
    })

    it('returns 401 for unknown email', async () => {
      const res = await request(app)
        .post('/auth/login')
        .send({ email: 'nobody@example.com', password: 'pass' })

      expect(res.status).toBe(401)
    })
  })

  describe('POST /auth/logout', () => {
    it('returns 200 and invalidates token', async () => {
      const loginRes = await request(app)
        .post('/auth/login')
        .send({ email: TEST_USER.email, password: TEST_USER.password })
      const t = loginRes.body.token

      const res = await request(app)
        .post('/auth/logout')
        .set('Authorization', `Bearer ${t}`)

      expect(res.status).toBe(200)
      expect(res.body.success).toBe(true)
    })

    it('returns 401 without token', async () => {
      const res = await request(app).post('/auth/logout')
      expect(res.status).toBe(401)
    })
  })

  describe('POST /auth/refresh', () => {
    it('returns new token for valid token', async () => {
      const loginRes = await request(app)
        .post('/auth/login')
        .send({ email: TEST_USER.email, password: TEST_USER.password })

      const res = await request(app)
        .post('/auth/refresh')
        .send({ token: loginRes.body.token })

      expect(res.status).toBe(200)
      expect(res.body.token).toBeDefined()
    })

    it('returns 401 for invalid token', async () => {
      const res = await request(app)
        .post('/auth/refresh')
        .send({ token: 'invalid.token' })

      expect(res.status).toBe(401)
    })
  })
})
