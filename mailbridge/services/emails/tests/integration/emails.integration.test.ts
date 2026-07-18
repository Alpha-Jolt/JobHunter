import request from 'supertest'
import { app } from '../../src/server'

const TOKEN = process.env.TEST_TOKEN ?? ''
const CREDENTIAL_ID = process.env.TEST_CREDENTIAL_ID ?? ''

describe('Emails API Integration', () => {
  let emailId: string

  describe('POST /api/emails/send', () => {
    it('queues email and returns email_id', async () => {
      const res = await request(app)
        .post('/api/emails/send')
        .set('Authorization', `Bearer ${TOKEN}`)
        .send({
          credential_id: CREDENTIAL_ID,
          to_email: 'recipient@example.com',
          subject: 'Hello {{name}}',
          html: '<p>Hi {{name}}</p>',
          variables: { name: 'Test User' }
        })

      expect([200, 202]).toContain(res.status)
      expect(res.body.success).toBe(true)
      expect(res.body.email_id).toBeDefined()
      expect(res.body.status).toBe('queued')
      emailId = res.body.email_id
    })

    it('returns 400 for missing credential_id', async () => {
      const res = await request(app)
        .post('/api/emails/send')
        .set('Authorization', `Bearer ${TOKEN}`)
        .send({ to_email: 'x@y.com', subject: 'Hi', html: '<p>Hi</p>' })

      expect(res.status).toBe(400)
    })

    it('returns 401 without token', async () => {
      const res = await request(app).post('/api/emails/send').send({})
      expect(res.status).toBe(401)
    })
  })

  describe('GET /api/emails', () => {
    it('returns paginated email logs', async () => {
      const res = await request(app)
        .get('/api/emails?page=1&limit=10')
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(200)
      expect(res.body.success).toBe(true)
      expect(Array.isArray(res.body.emails)).toBe(true)
      expect(typeof res.body.total).toBe('number')
    })
  })

  describe('GET /api/emails/:id', () => {
    it('returns email log by id', async () => {
      if (!emailId) return
      const res = await request(app)
        .get(`/api/emails/${emailId}`)
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(200)
      expect(res.body.email.email_id).toBe(emailId)
    })

    it('returns 404 for non-existent email', async () => {
      const res = await request(app)
        .get('/api/emails/00000000-0000-0000-0000-000000000000')
        .set('Authorization', `Bearer ${TOKEN}`)

      expect(res.status).toBe(404)
    })
  })
})
