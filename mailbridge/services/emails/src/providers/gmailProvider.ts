import { google } from 'googleapis'
import { IEmailProvider, SendOptions, SendResult } from './emailProvider'
import { ExternalServiceError } from '@mail-bridge/shared'

interface GmailTokens {
  access_token: string
  refresh_token?: string
  expiry_date?: number
}

export class GmailProvider implements IEmailProvider {
  constructor(
    private readonly clientId: string,
    private readonly clientSecret: string,
    private readonly redirectUri: string,
    private readonly tokens: GmailTokens
  ) {}

  async send(options: SendOptions): Promise<SendResult> {
    try {
      const auth = new google.auth.OAuth2(this.clientId, this.clientSecret, this.redirectUri)
      auth.setCredentials(this.tokens)

      const gmail = google.gmail({ version: 'v1', auth })

      const boundary = `boundary_${Date.now()}`
      let raw = [
        `To: ${options.to}`,
        `From: ${options.from}`,
        `Subject: ${options.subject}`,
        'MIME-Version: 1.0',
        `Content-Type: multipart/mixed; boundary="${boundary}"`,
        '',
        `--${boundary}`,
        'Content-Type: text/html; charset=utf-8',
        '',
        options.html
      ]

      for (const att of options.attachments ?? []) {
        raw = raw.concat([
          `--${boundary}`,
          `Content-Type: ${att.contentType}`,
          'Content-Transfer-Encoding: base64',
          `Content-Disposition: attachment; filename="${att.filename}"`,
          '',
          att.content.toString('base64')
        ])
      }
      raw.push(`--${boundary}--`)

      const encoded = Buffer.from(raw.join('\r\n')).toString('base64url')
      const result = await gmail.users.messages.send({ userId: 'me', requestBody: { raw: encoded } })

      return { messageId: result.data.id ?? 'unknown', timestamp: new Date() }
    } catch (err: any) {
      const errorMessage = err?.message || 'Unknown error'
      throw new ExternalServiceError(`Gmail send failed: ${errorMessage}`, 'GMAIL_SEND_FAILED')
    }
  }
}
