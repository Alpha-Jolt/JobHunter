import * as dotenv from 'dotenv'
dotenv.config()

export interface EmailsConfig {
  port: number
  nodeEnv: string
  databaseUrl: string
  redisUrl: string
  jwtSecret: string
  credentialMasterKey: string
  gmailClientId: string
  gmailClientSecret: string
  gmailRedirectUri: string
  outlookClientId: string
  outlookClientSecret: string
  outlookTenantId: string
  batchMaxSize: number
  logLevel: string
}

export function getConfig(): EmailsConfig {
  return {
    port: parseInt(process.env.PORT ?? '3003'),
    nodeEnv: process.env.NODE_ENV ?? 'development',
    databaseUrl: process.env.DATABASE_URL ?? '',
    redisUrl: process.env.REDIS_URL ?? 'redis://localhost:6379',
    jwtSecret: process.env.JWT_SECRET ?? '',
    credentialMasterKey: process.env.CREDENTIAL_MASTER_KEY ?? '',
    gmailClientId: process.env.GMAIL_CLIENT_ID ?? '',
    gmailClientSecret: process.env.GMAIL_CLIENT_SECRET ?? '',
    gmailRedirectUri: process.env.GMAIL_REDIRECT_URI ?? '',
    outlookClientId: process.env.OUTLOOK_CLIENT_ID ?? '',
    outlookClientSecret: process.env.OUTLOOK_CLIENT_SECRET ?? '',
    outlookTenantId: process.env.OUTLOOK_TENANT_ID ?? 'common',
    batchMaxSize: parseInt(process.env.BATCH_MAX_SIZE ?? '100'),
    logLevel: process.env.LOG_LEVEL ?? 'info'
  }
}
