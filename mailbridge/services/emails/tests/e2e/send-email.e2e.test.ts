/**
 * E2E: Full flow — register → login → add credential → send email → verify log
 * Requires running services (auth :3001, credentials :3002, emails :3003)
 * Set SERVICE_AUTH_URL, SERVICE_CREDENTIALS_URL, SERVICE_EMAILS_URL env vars
 */
import request from 'supertest'
import { app as authApp } from '../../../auth/src/server'
import { app as credApp } from '../../../credentials/src/server'
import { app as emailsApp } from '../../src/server'

const UNIQUE_EMAIL = `e2e-${Date.now()}@example.com`

describe('E2E: Register → Add Credential → Send Email', () => {
  let token: string
  let credentialId: string
  let emailId: string

  it('step 1: registers a new user', async () => {
    const res = await request(authApp)
      .post('/auth/register')
      .send({ email: UNIQUE_EMAIL, password: 'E2ePassword123!', workspace_name: 'E2E Workspace' })

    expect([200, 201]).toContain(res.status)
    expect(res.body.token).toBeDefined()
    token = res.body.token
  })

  it('step 2: adds SMTP credential', async () => {
    const res = await request(credApp)
      .post('/api/credentials/smtp')
      .set('Authorization', `Bearer ${token}`)
      .send({
        from_email: UNIQUE_EMAIL,
        host: 'smtp.example.com',
        port: 587,
        secure: false,
        user: UNIQUE_EMAIL,
        pass: 'smtp-password'
      })

    expect([200, 201]).toContain(res.status)
    expect(res.body.credential_id).toBeDefined()
    credentialId = res.body.credential_id
  })

  it('step 3: sends email and gets queued status', async () => {
    const res = await request(emailsApp)
      .post('/api/emails/send')
      .set('Authorization', `Bearer ${token}`)
      .send({
        credential_id: credentialId,
        to_email: 'recipient@example.com',
        subject: 'E2E Test {{ts}}',
        html: '<p>E2E test at {{ts}}</p>',
        variables: { ts: new Date().toISOString() }
      })

    expect([200, 202]).toContain(res.status)
    expect(res.body.status).toBe('queued')
    emailId = res.body.email_id
  })

  it('step 4: email log exists in emails service', async () => {
    const res = await request(emailsApp)
      .get(`/api/emails/${emailId}`)
      .set('Authorization', `Bearer ${token}`)

    expect(res.status).toBe(200)
    expect(res.body.email.email_id).toBe(emailId)
    expect(['queued', 'sent', 'failed']).toContain(res.body.email.status)
  })
})
