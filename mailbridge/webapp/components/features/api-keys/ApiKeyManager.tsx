'use client'

import { useState, useEffect } from 'react'
import { PageHeader } from '../../shared/PageHeader'
import { EmptyState } from '../../shared/EmptyState'
import { KeyRound, Plus, Trash2, Copy, CheckCircle2, AlertTriangle, Clock } from 'lucide-react'
import { withBasePath } from '@/lib/base-path'

interface ApiKey {
  api_key_id: string
  name: string
  scopes: string[]
  last_used_at: string | null
  expires_at: string | null
  revoked_at: string | null
  created_at: string
}

export function ApiKeyManager() {
  const [keys, setKeys] = useState<ApiKey[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [newScopes, setNewScopes] = useState<string[]>(['send'])
  const [expiresInDays, setExpiresInDays] = useState('0')
  const [creating, setCreating] = useState(false)

  const [newRawKey, setNewRawKey] = useState('')

  const [revokingId, setRevokingId] = useState<string | null>(null)

  const availableScopes = ['send', 'read', 'templates', 'credentials', 'admin']

  useEffect(() => {
    fetchKeys()
  }, [])

  async function fetchKeys() {
    try {
      const res = await fetch(withBasePath('/api/auth/api-keys'), {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (!res.ok) throw new Error('Failed to fetch API keys')
      const data = await res.json()
      setKeys(data.api_keys || [])
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setCreating(true)
    setError('')

    try {
      let expires_at: string | undefined = undefined
      const days = parseInt(expiresInDays)
      if (days > 0) {
        const d = new Date()
        d.setDate(d.getDate() + days)
        expires_at = d.toISOString()
      }

      const res = await fetch(withBasePath('/api/auth/api-keys'), {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name: newName, scopes: newScopes, expires_at })
      })

      if (!res.ok) {
        const errorData = await res.json()
        throw new Error(errorData.error || 'Failed to create key')
      }

      const data = await res.json()
      setNewRawKey(data.raw_key)
      setShowCreate(false)
      setNewName('')
      setNewScopes(['send'])
      setExpiresInDays('0')
      await fetchKeys()
    } catch (err: any) {
      setError(err.message)
    } finally {
      setCreating(false)
    }
  }

  async function handleRevoke(id: string) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) return
    setRevokingId(id)
    try {
      const res = await fetch(withBasePath(`/api/auth/api-keys/${id}`), {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      })
      if (!res.ok) throw new Error('Failed to revoke key')
      await fetchKeys()
    } catch (err: any) {
      alert(err.message)
    } finally {
      setRevokingId(null)
    }
  }

  function getExpiryStatus(expiresAt: string | null) {
    if (!expiresAt) return { text: 'Never', color: 'text-[var(--text-muted)]' }
    
    const d = new Date(expiresAt)
    const now = new Date()
    const diffDays = Math.ceil((d.getTime() - now.getTime()) / (1000 * 3600 * 24))

    if (diffDays <= 0) return { text: 'Expired', color: 'text-red-500' }
    if (diffDays <= 1) return { text: 'Expires soon', color: 'text-red-500' }
    if (diffDays <= 7) return { text: `Expires in ${diffDays} days`, color: 'text-amber-500' }
    return { text: `Expires in ${diffDays} days`, color: 'text-[var(--text-muted)]' }
  }

  const handleCopy = () => {
    navigator.clipboard.writeText(newRawKey)
    alert('Copied to clipboard')
  }

  return (
    <div className="max-w-4xl mx-auto py-8">
      <PageHeader 
        title="API Keys" 
        description="Manage API keys used to authenticate REST API requests."
        action={
          <button 
            onClick={() => setShowCreate(true)}
            className="inline-flex items-center gap-2 rounded-lg bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
          >
            <Plus className="h-4 w-4" />
            Create API Key
          </button>
        }
      />

      {error && (
        <div className="mb-6 rounded-lg bg-red-500/10 p-4 text-red-500 text-sm">
          {error}
        </div>
      )}

      {loading ? (
        <div className="animate-pulse flex flex-col gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-20 bg-[var(--surface)] rounded-xl border border-[var(--border)]"></div>
          ))}
        </div>
      ) : keys.length === 0 ? (
        <EmptyState 
          title="No API Keys" 
          description="Create an API key to allow external applications to authenticate with the API."
          icon={KeyRound}
        />
      ) : (
        <div className="flex flex-col gap-4">
          {keys.map(key => {
            const isRevoked = !!key.revoked_at
            const expiry = getExpiryStatus(key.expires_at)
            
            return (
              <div key={key.api_key_id} className={`flex flex-col sm:flex-row gap-4 p-5 rounded-xl border ${isRevoked ? 'bg-[var(--surface)]/50 border-[var(--border)]/50 opacity-60' : 'bg-[var(--surface)] border-[var(--border)]'} transition-colors`}>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-[var(--text)] truncate">{key.name}</h3>
                    {isRevoked && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-[var(--border)] text-[var(--text-muted)]">
                        Revoked
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-x-4 gap-y-2 mt-2 text-sm text-[var(--text-muted)]">
                    <div className="flex items-center gap-1.5">
                      <code className="text-xs font-mono bg-[var(--background)] px-1.5 py-0.5 rounded">
                        {key.api_key_id.substring(0, 8)}...
                      </code>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="font-medium">Scopes:</span>
                      {key.scopes.join(', ')}
                    </div>
                    {!isRevoked && (
                      <div className={`flex items-center gap-1.5 ${expiry.color}`}>
                        <Clock className="h-3.5 w-3.5" />
                        {expiry.text}
                      </div>
                    )}
                  </div>
                  <div className="text-xs text-[var(--text-muted)] mt-3">
                    Created {new Date(key.created_at).toLocaleDateString()} • 
                    Last used {key.last_used_at ? new Date(key.last_used_at).toLocaleDateString() : 'Never'}
                  </div>
                </div>
                
                {!isRevoked && (
                  <div className="flex items-center shrink-0">
                    <button
                      onClick={() => handleRevoke(key.api_key_id)}
                      disabled={revokingId === key.api_key_id}
                      className="p-2 text-[var(--text-muted)] hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors disabled:opacity-50"
                      title="Revoke Key"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl w-full max-w-md shadow-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-[var(--border)]">
              <h3 className="text-lg font-medium">Create API Key</h3>
            </div>
            
            <form onSubmit={handleCreate} className="p-6">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. JobHunter Production"
                    className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
                    value={newName}
                    onChange={e => setNewName(e.target.value)}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-1">Expiration</label>
                  <select
                    className="w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm outline-none focus:border-[var(--primary)]"
                    value={expiresInDays}
                    onChange={e => setExpiresInDays(e.target.value)}
                  >
                    <option value="0">Never (No expiry)</option>
                    <option value="30">30 days</option>
                    <option value="60">60 days</option>
                    <option value="90">90 days</option>
                    <option value="365">1 year</option>
                  </select>
                </div>

                <div className="bg-blue-500/10 p-3 rounded-lg border border-blue-500/20">
                  <div className="flex gap-2 text-blue-500">
                    <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
                    <p className="text-xs">
                      <strong>Best Practice:</strong> Rotate API keys every 30–90 days for optimal security. You will receive notifications when a key is approaching its expiration date.
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Scopes</label>
                  <div className="space-y-2">
                    {availableScopes.map(scope => (
                      <label key={scope} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          className="rounded border-[var(--border)] text-[var(--primary)] focus:ring-[var(--primary)]"
                          checked={newScopes.includes(scope)}
                          onChange={(e) => {
                            if (e.target.checked) setNewScopes([...newScopes, scope])
                            else setNewScopes(newScopes.filter(s => s !== scope))
                          }}
                        />
                        <span className="text-sm">{scope}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCreate(false)}
                  className="px-4 py-2 text-sm font-medium text-[var(--text-muted)] hover:text-[var(--text)]"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating || newScopes.length === 0}
                  className="px-4 py-2 text-sm font-medium text-white bg-[var(--primary)] rounded-lg hover:bg-[var(--primary-hover)] disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Key'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {newRawKey && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-[var(--surface)] border border-[var(--border)] rounded-xl w-full max-w-md shadow-xl overflow-hidden">
            <div className="p-6">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-green-500/10 mb-4">
                <CheckCircle2 className="h-6 w-6 text-green-500" />
              </div>
              <h3 className="text-xl font-medium text-center mb-2">API Key Created</h3>
              <p className="text-sm text-[var(--text-muted)] text-center mb-6">
                Please copy your API key now. For your security, it will never be shown again.
              </p>
              
              <div className="relative mb-6">
                <input
                  type="text"
                  readOnly
                  value={newRawKey}
                  className="w-full rounded-lg border border-green-500/30 bg-green-500/5 px-4 py-3 text-sm font-mono text-[var(--text)] outline-none pr-12"
                />
                <button
                  onClick={handleCopy}
                  className="absolute right-2 top-2 p-1.5 text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"
                >
                  <Copy className="h-5 w-5" />
                </button>
              </div>

              <button
                onClick={() => setNewRawKey('')}
                className="w-full px-4 py-2 text-sm font-medium text-[var(--surface)] bg-[var(--text)] rounded-lg hover:bg-[var(--text-muted)] transition-colors"
              >
                I have saved my API key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
