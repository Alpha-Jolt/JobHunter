import { Pool } from 'pg'
import axios from 'axios'
import { attemptDelivery } from '../../src/webhookDispatcher'
import { WebhookDelivery } from '@mail-bridge/shared'
import { WebhooksService } from '../../src/webhooks.service'

jest.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

const mockQuery = jest.fn()
const mockPool = { query: mockQuery } as unknown as Pool

const MASTER_KEY = '0'.repeat(64)
const service = new WebhooksService(mockPool, MASTER_KEY)

const baseDelivery: WebhookDelivery = {
  delivery_id: 'd1',
  webhook_id: 'wh1',
  email_id: 'e1',
  event: 'email.sent',
  payload: { event: 'email.sent', workspace_id: 'ws1' },
  status: 'pending',
  attempts: 0,
  next_retry_at: null,
  last_error: null,
  delivered_at: null,
  created_at: new Date()
}

beforeEach(() => { mockQuery.mockReset(); mockedAxios.post.mockReset() })

describe('webhookDispatcher', () => {
  describe('attemptDelivery', () => {
    it('POSTs payload to webhook URL', async () => {
      mockedAxios.post.mockResolvedValueOnce({ status: 200 })
      mockQuery.mockResolvedValueOnce({ rows: [] }) // UPDATE delivered
      await attemptDelivery(baseDelivery, 'https://example.com/hook', 'secret', mockPool)
      expect(mockedAxios.post).toHaveBeenCalledWith(
        'https://example.com/hook',
        baseDelivery.payload,
        expect.objectContaining({ headers: expect.objectContaining({ 'X-Mail-Bridge-Signature': expect.stringMatching(/^sha256=/) }) })
      )
    })

    it('includes correct HMAC-SHA256 signature header', async () => {
      mockedAxios.post.mockResolvedValueOnce({ status: 200 })
      mockQuery.mockResolvedValueOnce({ rows: [] })
      await attemptDelivery(baseDelivery, 'https://example.com/hook', 'my-secret', mockPool)
      const call = mockedAxios.post.mock.calls[0]
      const headers = (call[2] as { headers: Record<string, string> }).headers
      expect(headers['X-Mail-Bridge-Signature']).toMatch(/^sha256=[a-f0-9]{64}$/)
    })

    it('marks delivery as delivered on 2xx response', async () => {
      mockedAxios.post.mockResolvedValueOnce({ status: 200 })
      mockQuery.mockResolvedValueOnce({ rows: [] })
      await attemptDelivery(baseDelivery, 'https://example.com/hook', 'secret', mockPool)
      expect(mockQuery).toHaveBeenCalledWith(
        expect.stringContaining("status = 'delivered'"),
        expect.arrayContaining(['d1'])
      )
    })

    it('increments attempts and sets next_retry_at on failure', async () => {
      mockedAxios.post.mockRejectedValueOnce(new Error('timeout'))
      mockQuery.mockResolvedValueOnce({ rows: [] })
      await attemptDelivery(baseDelivery, 'https://example.com/hook', 'secret', mockPool)
      expect(mockQuery).toHaveBeenCalledWith(
        expect.stringContaining('next_retry_at'),
        expect.arrayContaining([1])
      )
    })

    it('marks delivery as failed after MAX_ATTEMPTS', async () => {
      const maxedDelivery = { ...baseDelivery, attempts: 4 }
      mockedAxios.post.mockRejectedValueOnce(new Error('timeout'))
      mockQuery.mockResolvedValueOnce({ rows: [] })
      await attemptDelivery(maxedDelivery, 'https://example.com/hook', 'secret', mockPool)
      expect(mockQuery).toHaveBeenCalledWith(
        expect.stringContaining("status = 'failed'"),
        expect.arrayContaining([5])
      )
    })
  })

  describe('WebhooksService.buildSignature', () => {
    it('returns sha256= prefixed HMAC', () => {
      const sig = WebhooksService.buildSignature('secret', '{"test":1}')
      expect(sig).toMatch(/^sha256=[a-f0-9]{64}$/)
    })
  })
})
