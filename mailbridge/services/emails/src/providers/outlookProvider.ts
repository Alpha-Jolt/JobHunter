import { Client } from '@microsoft/microsoft-graph-client'
import { Pool } from 'pg'
import { getOutlookAccessToken, OutlookConfig } from '@mail-bridge/shared'
import { IEmailProvider, SendOptions, SendResult } from './emailProvider'

export class OutlookProvider implements IEmailProvider {
  constructor(
    private readonly credentialId: string,
    private readonly encryptedValue: string,
    private readonly keyId: string,
    private readonly outlookConfig: OutlookConfig,
    private readonly pool: Pool
  ) {}

  async send(options: SendOptions): Promise<SendResult> {
    const accessToken = await getOutlookAccessToken(
      this.encryptedValue,
      this.credentialId,
      this.keyId,
      this.outlookConfig,
      this.pool
    )

    const client = Client.init({ authProvider: (done) => done(null, accessToken) })

    const message = {
      subject: options.subject,
      body: { contentType: 'HTML', content: options.html },
      toRecipients: [{ emailAddress: { address: options.to } }],
      from: { emailAddress: { address: options.from } }
    }

    const response = await client.api('/me/sendMail').post({ message, saveToSentItems: false })

    return {
      messageId: response?.id ?? `outlook-${Date.now()}`,
      timestamp: new Date()
    }
  }
}
