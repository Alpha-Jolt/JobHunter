import nodemailer from 'nodemailer'
import { IEmailProvider, SendOptions, SendResult } from './emailProvider'
import { ExternalServiceError } from '@mail-bridge/shared'

interface SmtpConfig {
  host: string
  port: number
  secure: boolean
  user: string
  pass: string
}

export class SmtpProvider implements IEmailProvider {
  constructor(private readonly smtpConfig: SmtpConfig) {}

  async send(options: SendOptions): Promise<SendResult> {
    const transporter = nodemailer.createTransport({
      host: this.smtpConfig.host,
      port: this.smtpConfig.port,
      secure: this.smtpConfig.secure,
      auth: { user: this.smtpConfig.user, pass: this.smtpConfig.pass }
    })

    try {
      const info = await transporter.sendMail({
        from: options.from,
        to: options.to,
        subject: options.subject,
        html: options.html,
        attachments: options.attachments?.map(a => ({
          filename: a.filename,
          content: a.content,
          contentType: a.contentType
        }))
      })
      return { messageId: info.messageId, timestamp: new Date() }
    } catch (err) {
      throw new ExternalServiceError('SMTP send failed', 'SMTP_SEND_FAILED')
    }
  }
}
