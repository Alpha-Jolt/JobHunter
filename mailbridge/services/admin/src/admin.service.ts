import { Pool } from 'pg'
import { NotFoundError, ConflictError } from '@mail-bridge/shared'
import { User, FlatRole } from '@mail-bridge/shared'

export class AdminService {
  constructor(private readonly pool: Pool) {}

  async listUsers(workspaceId: string): Promise<Omit<User, 'password_hash'>[]> {
    const result = await this.pool.query<Omit<User, 'password_hash'>>(
      `SELECT user_id, email, workspace_id, role, created_at, updated_at
       FROM users WHERE workspace_id = $1 AND deleted_at IS NULL ORDER BY created_at`,
      [workspaceId]
    )
    return result.rows
  }

  async inviteUser(email: string, role: FlatRole, workspaceId: string): Promise<Omit<User, 'password_hash'>> {
    const existing = await this.pool.query('SELECT user_id FROM users WHERE email = $1', [email])
    if (existing.rows.length > 0) throw new ConflictError('User already exists', 'USER_EXISTS')

    const result = await this.pool.query<Omit<User, 'password_hash'>>(
      `INSERT INTO users (email, password_hash, workspace_id, role)
       VALUES ($1, 'INVITE_PENDING', $2, $3)
       RETURNING user_id, email, workspace_id, role, created_at, updated_at`,
      [email, workspaceId, role]
    )
    return result.rows[0]
  }

  async changeRole(userId: string, role: FlatRole, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      'UPDATE users SET role = $1, updated_at = NOW() WHERE user_id = $2 AND workspace_id = $3 AND deleted_at IS NULL',
      [role, userId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('User not found')
  }

  async removeUser(userId: string, workspaceId: string): Promise<void> {
    const result = await this.pool.query(
      'UPDATE users SET deleted_at = NOW() WHERE user_id = $1 AND workspace_id = $2 AND deleted_at IS NULL',
      [userId, workspaceId]
    )
    if (result.rowCount === 0) throw new NotFoundError('User not found')
  }
}
