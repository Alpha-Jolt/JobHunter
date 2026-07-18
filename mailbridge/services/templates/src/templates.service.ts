import { Pool } from 'pg'
import { NotFoundError } from '@mail-bridge/shared'
import { EmailTemplate, EmailTemplateVersion, ValidationRules } from '@mail-bridge/shared'

export interface CreateTemplateInput {
  name: string
  subject: string
  html: string
  variables?: string[]
  validation_rules?: ValidationRules
}

export class TemplatesService {
  constructor(private readonly pool: Pool) {}

  async create(input: CreateTemplateInput, workspaceId: string, userId: string): Promise<EmailTemplate> {
    const result = await this.pool.query<EmailTemplate>(
      `INSERT INTO email_templates (workspace_id, name, subject, html, variables, validation_rules, created_by)
       VALUES ($1, $2, $3, $4, $5, $6, $7) RETURNING *`,
      [
        workspaceId, input.name, input.subject, input.html,
        JSON.stringify(input.variables ?? []),
        JSON.stringify(input.validation_rules ?? {}),
        userId
      ]
    )
    return result.rows[0]
  }

  async list(workspaceId: string): Promise<EmailTemplate[]> {
    const result = await this.pool.query<EmailTemplate>(
      'SELECT * FROM email_templates WHERE workspace_id = $1 ORDER BY created_at DESC',
      [workspaceId]
    )
    return result.rows
  }

  async update(
    templateId: string,
    workspaceId: string,
    input: Partial<CreateTemplateInput>,
    userId: string
  ): Promise<EmailTemplate> {
    const client = await this.pool.connect()
    try {
      await client.query('BEGIN')

      // Snapshot current version before update
      const current = await client.query<EmailTemplate>(
        'SELECT * FROM email_templates WHERE template_id = $1 AND workspace_id = $2',
        [templateId, workspaceId]
      )
      if (!current.rows[0]) throw new NotFoundError('Template not found')

      const t = current.rows[0]
      await client.query(
        `INSERT INTO email_template_versions
           (template_id, version, name, subject, html, variables, validation_rules, snapshotted_by)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
         ON CONFLICT (template_id, version) DO NOTHING`,
        [t.template_id, t.version, t.name, t.subject, t.html,
         JSON.stringify(t.variables), JSON.stringify(t.validation_rules ?? {}), userId]
      )

      const result = await client.query<EmailTemplate>(
        `UPDATE email_templates SET
           name = COALESCE($1, name),
           subject = COALESCE($2, subject),
           html = COALESCE($3, html),
           variables = COALESCE($4, variables),
           validation_rules = COALESCE($5, validation_rules),
           version = version + 1,
           updated_at = NOW()
         WHERE template_id = $6 AND workspace_id = $7 RETURNING *`,
        [
          input.name ?? null, input.subject ?? null, input.html ?? null,
          input.variables ? JSON.stringify(input.variables) : null,
          input.validation_rules ? JSON.stringify(input.validation_rules) : null,
          templateId, workspaceId
        ]
      )

      await client.query('COMMIT')
      return result.rows[0]
    } catch (err) {
      await client.query('ROLLBACK')
      throw err
    } finally {
      client.release()
    }
  }

  async getVersions(
    templateId: string,
    workspaceId: string,
    page = 1,
    limit = 20
  ): Promise<{ versions: EmailTemplateVersion[]; total: number }> {
    // Verify template belongs to workspace
    const check = await this.pool.query(
      'SELECT 1 FROM email_templates WHERE template_id = $1 AND workspace_id = $2',
      [templateId, workspaceId]
    )
    if (!check.rows[0]) throw new NotFoundError('Template not found')

    const offset = (page - 1) * limit
    const [rows, count] = await Promise.all([
      this.pool.query<EmailTemplateVersion>(
        `SELECT * FROM email_template_versions WHERE template_id = $1
         ORDER BY version DESC LIMIT $2 OFFSET $3`,
        [templateId, limit, offset]
      ),
      this.pool.query<{ count: string }>(
        'SELECT COUNT(*) FROM email_template_versions WHERE template_id = $1',
        [templateId]
      )
    ])
    return { versions: rows.rows, total: parseInt(count.rows[0].count) }
  }

  async rollback(
    templateId: string,
    targetVersion: number,
    workspaceId: string,
    userId: string
  ): Promise<EmailTemplate> {
    const client = await this.pool.connect()
    try {
      await client.query('BEGIN')

      const snapshot = await client.query<EmailTemplateVersion>(
        `SELECT * FROM email_template_versions WHERE template_id = $1 AND version = $2`,
        [templateId, targetVersion]
      )
      if (!snapshot.rows[0]) throw new NotFoundError(`Version ${targetVersion} not found`)

      const current = await client.query<EmailTemplate>(
        'SELECT * FROM email_templates WHERE template_id = $1 AND workspace_id = $2',
        [templateId, workspaceId]
      )
      if (!current.rows[0]) throw new NotFoundError('Template not found')

      const t = current.rows[0]
      const s = snapshot.rows[0]

      // Snapshot current state before rollback
      await client.query(
        `INSERT INTO email_template_versions
           (template_id, version, name, subject, html, variables, validation_rules, snapshotted_by)
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
         ON CONFLICT (template_id, version) DO NOTHING`,
        [t.template_id, t.version, t.name, t.subject, t.html,
         JSON.stringify(t.variables), JSON.stringify(t.validation_rules ?? {}), userId]
      )

      // Apply rollback — new version = current_max + 1
      const result = await client.query<EmailTemplate>(
        `UPDATE email_templates SET
           name = $1, subject = $2, html = $3, variables = $4,
           validation_rules = $5, version = version + 1, updated_at = NOW()
         WHERE template_id = $6 AND workspace_id = $7 RETURNING *`,
        [
          s.name, s.subject, s.html,
          JSON.stringify(s.variables), JSON.stringify(s.validation_rules ?? {}),
          templateId, workspaceId
        ]
      )

      await client.query('COMMIT')
      return result.rows[0]
    } catch (err) {
      await client.query('ROLLBACK')
      throw err
    } finally {
      client.release()
    }
  }

  async remove(templateId: string, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      'DELETE FROM email_templates WHERE template_id = $1 AND workspace_id = $2',
      [templateId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('Template not found')
  }
}
