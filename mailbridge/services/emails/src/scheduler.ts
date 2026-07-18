import cron from 'node-cron'
import { Pool } from 'pg'
import { enqueue, logger } from '@mail-bridge/shared'

/**
 * Runs every minute. Picks up pending scheduled emails using
 * SELECT FOR UPDATE SKIP LOCKED to be safe for multi-instance deployments.
 */
export function startScheduler(pool: Pool): void {
  cron.schedule('* * * * *', async () => {
    const client = await pool.connect()
    try {
      await client.query('BEGIN')

      const { rows } = await client.query<{
        scheduled_id: string
        credential_id: string
        workspace_id: string
        to_email: string
        subject: string
        html: string
        variables: Record<string, unknown>
        template_id: string | null
      }>(
        `SELECT scheduled_id, credential_id, workspace_id, to_email, subject, html, variables, template_id
         FROM scheduled_emails
         WHERE status = 'pending' AND scheduled_at <= NOW()
         FOR UPDATE SKIP LOCKED
         LIMIT 50`
      )

      for (const row of rows) {
        // Insert email_log record
        const logResult = await client.query<{ email_id: string }>(
          `INSERT INTO email_logs (workspace_id, credential_id, to_email, from_email, subject, template_id, status)
           SELECT $1, $2, $3, c.from_email, $4, $5, 'queued'
           FROM credentials c WHERE c.credential_id = $2
           RETURNING email_id`,
          [row.workspace_id, row.credential_id, row.to_email, row.subject, row.template_id]
        )

        if (logResult.rows.length === 0) continue

        await enqueue({
          emailLogId: logResult.rows[0].email_id,
          credentialId: row.credential_id,
          workspaceId: row.workspace_id,
          to: row.to_email,
          from: '',
          subject: row.subject,
          html: row.html
        })

        await client.query(
          `UPDATE scheduled_emails SET status = 'queued' WHERE scheduled_id = $1`,
          [row.scheduled_id]
        )
      }

      await client.query('COMMIT')

      if (rows.length > 0) {
        logger.info({ count: rows.length }, 'Scheduler: enqueued scheduled emails')
      }
    } catch (err) {
      await client.query('ROLLBACK')
      logger.error({ err }, 'Scheduler: error processing scheduled emails')
    } finally {
      client.release()
    }
  })

  logger.info('Scheduler started — checking every minute')
}
