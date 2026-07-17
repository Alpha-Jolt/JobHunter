import { Pool } from 'pg'
import { getSharedConfig } from '../config'

let pool: Pool | null = null

export function getPool(): Pool {
  if (!pool) {
    const config = getSharedConfig()
    pool = new Pool({ connectionString: config.databaseUrl, max: 10 })
  }
  return pool
}

export async function closePool(): Promise<void> {
  if (pool) {
    await pool.end()
    pool = null
  }
}
