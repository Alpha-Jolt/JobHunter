import request from 'supertest'
import { app } from '../../src/server'

// Requires a valid JWT from auth service — set via TEST_TOKEN env var or run after auth integration
const TOKEN = process.env.TEST_TOKEN ?? ''

const SMTP_PAYLOAD = {
  from_email: 'test@example.com',
  host: 'smtp.example.com',
  port: 587,
  secure: false,
  user: 'test@example.com',
  pass: 'test-password'
}

describe('Credentials API Integration', () => {
  let credentialId: string

  describe('POST /api/credentials/smtp', () => {
    it('adds SMTP credential and returns credential_id', async () => {
      const res = await request(app)
        .post('/api/credentials/smtp')
        .set('Authorization', `Bearer ${TOKEN}`)
        .send(SMTP_PAYLOAD)

      expect([200, 201]).toContain(res.status)
      expect(res.body.success).toBe(true)
      expect(res.body.credential_id).toBeDefined()
      expect(res.body.encrypted_value).toBeUndefined() // never returned
      credentialId = res.body.credential_id
    })

    it('returns 400 for missing fields', async () => {
      const res = await request(app)
        .post('/api/credentials/smtp')
        .set('Authorization', `Bearer ${TOKEN}`)
        .send({ from_email: 'x@y.com' })

      expect(res.status).toBe(400)
      expect(res.body.error.code).toBe('INVALID_PAYLOAD')
    })

    it('returns 401 without token', async () => {
      const res = await request(app).post('/api/credentials/smtp').send(SMTP_PAYLOAD)
      expect(res.status).toBe(401)
    })
  })

  describe('GET /api/credentials', () => {
    it('lists credentials without encrypted_value', async () => {
      const res = await request(app)
        .get('/api/credentials')
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(200)
      expect(res.body.success).toBe(true)
      expect(Array.isArray(res.body.credentials)).toBe(true)
      for (const c of res.body.credentials) {
        expect(c.encrypted_value).toBeUndefined()
      }
    })
  })

  describe('DELETE /api/credentials/:id', () => {
    it('removes credential', async () => {
      if (!credentialId) return
      const res = await request(app)
        .delete(`/api/credentials/${credentialId}`)
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(200)
      expect(res.body.success).toBe(true)
    })

    it('returns 404 for non-existent credential', async () => {
      const res = await request(app)
        .delete('/api/credentials/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(404)
    })
  })
})
