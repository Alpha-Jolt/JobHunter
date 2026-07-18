import { Router, Request, Response, NextFunction } from 'express'
import { Pool } from 'pg'
import { google } from 'googleapis'
import { decrypt } from './credentialManager'
import { logger, getRedisClient } from '@mail-bridge/shared'

export function createInboundRouter(pool: Pool): Router {
  const router = Router()
  const redis = getRedisClient()

  router.post('/gmail-push', async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Gmail Pub/Sub push notification — respond 204 immediately to acknowledge
      res.status(204).send()

      const data = req.body.message?.data
      if (!data) return

      const payload = JSON.parse(Buffer.from(data, 'base64').toString('utf-8'))
      const { emailAddress, historyId } = payload

      if (!emailAddress || !historyId) return

      logger.info({ emailAddress, historyId }, 'Received Gmail push notification')

      // Look up the Gmail credential for this email address
      const credResult = await pool.query(
        `SELECT * FROM credentials
         WHERE from_email = $1 AND provider_type = 'gmail' AND is_active = TRUE
         LIMIT 1`,
        [emailAddress]
      )
      if (credResult.rows.length === 0) {
        logger.warn({ emailAddress }, 'No active Gmail credential found for push notification')
        return
      }

      const credential = credResult.rows[0]
      const masterKey = process.env.CREDENTIAL_MASTER_KEY ?? ''
      const plaintext = decrypt(credential.encrypted_value, masterKey, credential.encryption_key_id)
      const tokens = JSON.parse(plaintext)

      // Fetch new messages using history.list since last known historyId
      const auth = new google.auth.OAuth2(
        process.env.GMAIL_CLIENT_ID,
        process.env.GMAIL_CLIENT_SECRET,
        process.env.GMAIL_REDIRECT_URI
      )
      auth.setCredentials(tokens)
      const gmail = google.gmail({ version: 'v1', auth })

      // Get the stored historyId for this credential (stored in metadata)
      const storedHistoryId = credential.metadata?.lastHistoryId as string | undefined
      const startHistoryId = storedHistoryId ?? historyId

      const historyRes = await gmail.users.history.list({
        userId: 'me',
        startHistoryId,
        historyTypes: ['messageAdded'],
        labelId: 'INBOX'
      })

      const messages = historyRes.data.history?.flatMap(h => h.messagesAdded ?? []) ?? []

      for (const added of messages) {
        const msgId = added.message?.id
        if (!msgId) continue

        try {
          const msg = await gmail.users.messages.get({
            userId: 'me',
            id: msgId,
            format: 'metadata',
            metadataHeaders: ['From', 'Subject', 'Date']
          })

          const headers = msg.data.payload?.headers ?? []
          const from = headers.find(h => h.name === 'From')?.value ?? emailAddress
          const subject = headers.find(h => h.name === 'Subject')?.value ?? null
          const dateHeader = headers.find(h => h.name === 'Date')?.value
          const receivedAt = dateHeader ? new Date(dateHeader) : new Date()

          // Write to incoming_email_logs
          await pool.query(
            `INSERT INTO incoming_email_logs (workspace_id, credential_id, from_address, subject, received_at)
             VALUES ($1, $2, $3, $4, $5)
             ON CONFLICT DO NOTHING`,
            [credential.workspace_id, credential.credential_id, from, subject, receivedAt]
          )

          // Publish webhook event
          await redis.publish('webhook:events', JSON.stringify({
            workspaceId: credential.workspace_id,
            event: 'email.received',
            payload: { from, subject, received_at: receivedAt }
          }))

          logger.info({ from, subject, workspaceId: credential.workspace_id }, 'Inbound Gmail email logged')
        } catch (msgErr) {
          logger.error({ msgErr, msgId }, 'Failed to fetch Gmail message details')
        }
      }

      // Update stored historyId for next time
      await pool.query(
        `UPDATE credentials SET metadata = metadata || $1 WHERE credential_id = $2`,
        [JSON.stringify({ lastHistoryId: historyId }), credential.credential_id]
      )
    } catch (err) {
      logger.error({ err }, 'Gmail push handler error')
    }
  })

  router.post('/outlook-push', async (req: Request, res: Response, next: NextFunction) => {
    try {
      // Validation request from Microsoft Graph
      if (req.query.validationToken) {
        return res.status(200).send(req.query.validationToken)
      }

      // Acknowledge immediately
      res.status(202).send()

      const notifications = req.body.value
      if (!notifications?.length) return

      for (const notification of notifications) {
        logger.info({ resourceData: notification.resourceData }, 'Received Outlook push notification')
        // Full implementation: fetch message from Graph API and write to incoming_email_logs
        // Similar pattern to Gmail handler above — use credential lookup by subscription ID
      }
    } catch (err) {
      logger.error({ err }, 'Outlook push handler error')
      next(err)
    }
  })

  return router
}
