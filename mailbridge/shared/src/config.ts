import * as dotenv from 'dotenv'
dotenv.config()

export interface SharedConfig {
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  jwtExpiresIn: string
  credentialMasterKey: string
  logLevel: string
}

function requireEnv(key: string): string {
  const val = process.env[key]
  if (!val) throw new Error(`Missing required env var: ${key}`)
  return val
}

function optional(key: string, fallback: string): string {
  return process.env[key] ?? fallback
}

export function getSharedConfig(): SharedConfig {
  return {
    nodeEnv: optional('NODE_ENV', 'development'),
    databaseUrl: requireEnv('DATABASE_URL'),
    redisUrl: optional('REDIS_URL', 'redis://localhost:6379'),
    jwtSecret: requireEnv('JWT_SECRET'),
    jwtExpiresIn: optional('JWT_EXPIRES_IN', '24h'),
    credentialMasterKey: requireEnv('CREDENTIAL_MASTER_KEY'),
    logLevel: optional('LOG_LEVEL', 'info')
  }
}
