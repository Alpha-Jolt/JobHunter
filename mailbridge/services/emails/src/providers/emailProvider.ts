export interface SendOptions {
  to: string
  from: string
  subject: string
  html: string
  attachments?: { filename: string; content: Buffer; contentType: string }[]
}

export interface SendResult {
  messageId: string
  timestamp: Date
}

export interface IEmailProvider {
  send(options: SendOptions): Promise<SendResult>
}
