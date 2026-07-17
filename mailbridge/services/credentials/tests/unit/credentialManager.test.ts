import { encrypt, decrypt } from '../../src/credentialManager'

const MASTER_KEY = '0'.repeat(64)
const KEY_ID = 'test-key-id-1'

describe('credentialManager', () => {
  it('encrypts and decrypts roundtrip', () => {
    const plaintext = JSON.stringify({ host: 'smtp.example.com', port: 587, user: 'u', pass: 'p' })
    const ciphertext = encrypt(plaintext, MASTER_KEY, KEY_ID)
    expect(decrypt(ciphertext, MASTER_KEY, KEY_ID)).toBe(plaintext)
  })

  it('different keyIds produce different ciphertext', () => {
    const plaintext = 'same-plaintext'
    const c1 = encrypt(plaintext, MASTER_KEY, 'key-1')
    const c2 = encrypt(plaintext, MASTER_KEY, 'key-2')
    expect(c1).not.toBe(c2)
  })

  it('same plaintext produces different ciphertext each call (random IV)', () => {
    const c1 = encrypt('hello', MASTER_KEY, KEY_ID)
    const c2 = encrypt('hello', MASTER_KEY, KEY_ID)
    expect(c1).not.toBe(c2)
  })

  it('throws on tampered ciphertext', () => {
    const ciphertext = encrypt('secret', MASTER_KEY, KEY_ID)
    const tampered = Buffer.from(ciphertext, 'base64')
    tampered[tampered.length - 1] ^= 0xff
    expect(() => decrypt(tampered.toString('base64'), MASTER_KEY, KEY_ID)).toThrow()
  })
})
