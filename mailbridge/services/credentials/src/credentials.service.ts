import { Pool } from 'pg'
import { randomUUID } from 'crypto'
import { google } from 'googleapis'
import { encrypt, decrypt } from './credentialManager'
import { NotFoundError, ExternalServiceError, logger } from '@mail-bridge/shared'
import { Credential } from '@mail-bridge/shared'
import { CredentialsConfig } from './config'
import { exchangeOutlookCode, getOutlookConsentUrl } from './outlookOAuth'

export interface SmtpInput {
  from_email: string
  host: string
  port: number
  secure: boolean
  user: string
  pass: string
  imap_host?: string
  imap_port?: number
  imap_secure?: boolean
  imap_sync_mode?: 'idle' | 'polling'
  imap_poll_interval?: number
}

export class CredentialsService {
  private oauth2Client

  constructor(
    private readonly pool: Pool,
    private readonly config: CredentialsConfig
  ) {
    this.oauth2Client = new google.auth.OAuth2(
      config.gmailClientId,
      config.gmailClientSecret,
      config.gmailRedirectUri
    )
  }

  getGmailAuthUrl(workspaceId: string): string {
    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
      ],
      prompt: 'consent',
      state: workspaceId
    })
  }

  async handleGmailCallback(code: string, workspaceId: string): Promise<Credential> {
    const { tokens } = await this.oauth2Client.getToken(code)
    if (!tokens.access_token) throw new ExternalServiceError('Gmail OAuth failed — no access token', 'OAUTH_FAILED')

    const keyId = randomUUID()
    const encrypted = encrypt(JSON.stringify(tokens), this.config.credentialMasterKey, keyId)

    // Get email from OAuth2 userinfo
    this.oauth2Client.setCredentials(tokens)
    const oauth2api = google.oauth2({ version: 'v2', auth: this.oauth2Client })
    const userinfo = await oauth2api.userinfo.get()
    const from_email = userinfo.data.email ?? ''

    const result = await this.pool.query<Credential>(
      `INSERT INTO credentials (workspace_id, provider_type, from_email, encrypted_value, encryption_key_id)
       VALUES ($1, 'gmail', $2, $3, $4) RETURNING *`,
      [workspaceId, from_email, encrypted, keyId]
    )

    // Register Gmail Pub/Sub watch so push notifications are delivered
    // Requires a Cloud Pub/Sub topic granted publish rights to gmail-api-push@system.gserviceaccount.com
    if (this.config.gmailPubSubTopic) {
      try {
        const gmail = google.gmail({ version: 'v1', auth: this.oauth2Client })
        await gmail.users.watch({
          userId: 'me',
          requestBody: {
            topicName: this.config.gmailPubSubTopic,
            labelIds: ['INBOX']
          }
        })
      } catch (watchErr) {
        // Non-fatal — log and continue; inbound push won't work but send still functions
        logger.warn({ watchErr, workspaceId }, 'Gmail watch registration failed — inbound push disabled')
      }
    }

    return result.rows[0]
  }

  async addSmtp(input: SmtpInput, workspaceId: string): Promise<Omit<Credential, 'encrypted_value'>> {
    const keyId = randomUUID()
    const encrypted = encrypt(JSON.stringify({
      host: input.host, port: input.port, secure: input.secure,
      user: input.user, pass: input.pass
    }), this.config.credentialMasterKey, keyId)

    const result = await this.pool.query<Credential>(
      `INSERT INTO credentials (workspace_id, provider_type, from_email, encrypted_value, encryption_key_id, imap_host, imap_port, imap_secure, imap_sync_mode, imap_poll_interval)
       VALUES ($1, 'smtp', $2, $3, $4, $5, $6, $7, $8, $9) RETURNING credential_id, workspace_id, provider_type, from_email, is_active, last_used_at, metadata, created_at, encryption_key_id, imap_host, imap_port, imap_secure, imap_sync_mode, imap_poll_interval`,
      [workspaceId, input.from_email, encrypted, keyId, input.imap_host || null, input.imap_port || null, input.imap_secure || null, input.imap_sync_mode || null, input.imap_poll_interval || null]
    )
    return result.rows[0]
  }

  async list(workspaceId: string): Promise<Omit<Credential, 'encrypted_value'>[]> {
    const result = await this.pool.query<Omit<Credential, 'encrypted_value'>>(
      `SELECT credential_id, workspace_id, provider_type, from_email, is_active, last_used_at, metadata, created_at, encryption_key_id, imap_host, imap_port, imap_secure, imap_sync_mode, imap_poll_interval
       FROM credentials WHERE workspace_id = $1 AND is_active = TRUE ORDER BY created_at DESC`,
      [workspaceId]
    )
    return result.rows
  }

  async remove(credentialId: string, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      'UPDATE credentials SET is_active = FALSE WHERE credential_id = $1 AND workspace_id = $2',
      [credentialId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('Credential not found')
  }

  async getOutlookAuthUrl(workspaceId: string): Promise<string> {
    return await getOutlookConsentUrl(this.config, workspaceId)
  }

  async handleOutlookCallback(code: string, workspaceId: string): Promise<Credential> {
    const tokens = await exchangeOutlookCode(code, this.config)
    if (!tokens.access_token) throw new ExternalServiceError('Outlook OAuth failed — no access token', 'OAUTH_FAILED')

    const keyId = randomUUID()
    const encrypted = encrypt(JSON.stringify(tokens), this.config.credentialMasterKey, keyId)

    // Get email from Microsoft Graph
    const { Client } = await import('@microsoft/microsoft-graph-client')
    const client = Client.init({ authProvider: (done) => done(null, tokens.access_token) })
    const me = await client.api('/me').select('mail,userPrincipalName').get()
    const from_email: string = me.mail ?? me.userPrincipalName ?? ''

    const result = await this.pool.query<Credential>(
      `INSERT INTO credentials (workspace_id, provider_type, from_email, encrypted_value, encryption_key_id)
       VALUES ($1, 'outlook', $2, $3, $4) RETURNING *`,
      [workspaceId, from_email, encrypted, keyId]
    )
    return result.rows[0]
  }


  async registerGmailWatch(credentialId: string, workspaceId: string): Promise<void> {
    if (!this.config.gmailPubSubTopic) {
      throw new Error('GMAIL_PUBSUB_TOPIC is not configured')
    }

    const result = await this.pool.query<Credential>(
      'SELECT * FROM credentials WHERE credential_id = $1 AND workspace_id = $2 AND is_active = TRUE',
      [credentialId, workspaceId]
    )
    const credential = result.rows[0]
    if (!credential) throw new NotFoundError('Credential not found')
    if (credential.provider_type !== 'gmail') {
      throw new Error('Watch can only be registered for Gmail credentials')
    }

    const plaintext = decrypt(credential.encrypted_value, this.config.credentialMasterKey, credential.encryption_key_id)
    const tokens = JSON.parse(plaintext)

    this.oauth2Client.setCredentials(tokens)
    const gmail = google.gmail({ version: 'v1', auth: this.oauth2Client })

    const watchRes = await gmail.users.watch({
      userId: 'me',
      requestBody: {
        topicName: this.config.gmailPubSubTopic,
        labelIds: ['INBOX']
      }
    })

    logger.info({ credentialId, historyId: watchRes.data.historyId }, 'Gmail watch registered')

    // Store the historyId so the push handler knows where to start
    await this.pool.query(
      `UPDATE credentials SET metadata = metadata || $1 WHERE credential_id = $2`,
      [JSON.stringify({ lastHistoryId: watchRes.data.historyId }), credentialId]
    )
  }

  async getDecrypted(credentialId: string, workspaceId: string): Promise<{ credential: Credential; plaintext: string }> {
    const result = await this.pool.query<Credential>(
      'SELECT * FROM credentials WHERE credential_id = $1 AND workspace_id = $2 AND is_active = TRUE',
      [credentialId, workspaceId]
    )
    const credential = result.rows[0]
    if (!credential) throw new NotFoundError('Credential not found')
    const plaintext = decrypt(credential.encrypted_value, this.config.credentialMasterKey, credential.encryption_key_id)
    return { credential, plaintext }
  }
}
