import Redis from 'ioredis'
import { randomUUID } from 'crypto'
import { EmailJob } from '../models/types'
import { getSharedConfig } from '../config'
import { logger } from '../features/logging'

const QUEUE_KEY = 'mail:queue'
const MAX_RETRIES = 3

let client: Redis | null = null

export function getRedisClient(): Redis {
  if (!client) {
    const config = getSharedConfig()
    client = new Redis(config.redisUrl, { lazyConnect: true })
    client.on('error', (err) => {
      logger.error({ err }, '[ioredis] Connection error')
    })
  }
  return client
}

export async function closeRedis(): Promise<void> {
  if (client) {
    await client.quit()
    client = null
  }
}

export async function enqueue(job: Omit<EmailJob, 'jobId'>): Promise<string> {
  const jobId = randomUUID()
  const fullJob: EmailJob = { ...job, jobId }
  await getRedisClient().lpush(QUEUE_KEY, JSON.stringify(fullJob))
  return jobId
}

export async function dequeue(timeoutSeconds = 5): Promise<EmailJob | null> {
  const result = await getRedisClient().brpop(QUEUE_KEY, timeoutSeconds)
  if (!result) return null
  return JSON.parse(result[1]) as EmailJob
}

export { MAX_RETRIES, QUEUE_KEY }
