'use client'

import { useState } from 'react'
import { useCredentials, useRemoveCredential, useTestCredential } from '@/lib/hooks/useCredentials'
import { credentialsApi } from '@/lib/api/credentials'
import { PageHeader } from '@/components/shared/PageHeader'
import { CardSkeleton } from '@/components/shared/CardSkeleton'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { StatusBadge } from '@/components/shared/StatusBadge'
import Link from 'next/link'
import { Key, Plus, Trash2, CheckCircle, ExternalLink } from 'lucide-react'

export default function CredentialsPage() {
  const { data, isLoading } = useCredentials()
  const { mutate: remove } = useRemoveCredential()
  const { mutate: test, isPending: testing } = useTestCredential()
  const [testResult, setTestResult] = useState<Record<string, string>>({})

  async function handleOAuth(provider: 'gmail' | 'outlook') {
    const fn = provider === 'gmail' ? credentialsApi.gmailConnectUrl : credentialsApi.outlookConnectUrl
    const res = await fn()
    window.location.href = res.url
  }

  function handleTest(id: string) {
    test(id, {
      onSuccess: () => setTestResult(p => ({ ...p, [id]: 'ok' })),
      onError: () => setTestResult(p => ({ ...p, [id]: 'failed' }))
    })
  }

  return (
    <div>
      <PageHeader
        title="Credentials"
        description="Email provider credentials"
        action={
          <Link href="/credentials/new" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            <Plus className="h-4 w-4" /> Add credential
          </Link>
        }
      />

      <div className="mb-4 flex gap-2">
        <button onClick={() => handleOAuth('gmail')} className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">
          <ExternalLink className="h-3.5 w-3.5" /> Connect Gmail
        </button>
        <button onClick={() => handleOAuth('outlook')} className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">
          <ExternalLink className="h-3.5 w-3.5" /> Connect Outlook
        </button>
      </div>

      <ErrorBoundary feature="Credentials">
        {isLoading ? (
          <CardSkeleton count={3} />
        ) : data?.credentials.length === 0 ? (
          <EmptyState icon={Key} title="No credentials" description="Add an email credential to start sending" action={<Link href="/credentials/new" className="rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors">Add credential</Link>} />
        ) : (
          <div className="grid gap-3">
            {data?.credentials.map(c => (
              <div key={c.credential_id} className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-4 shadow-base">
                <div>
                  <p className="font-medium text-[var(--text)]">{c.from_email}</p>
                  <p className="text-sm text-[var(--text-muted)] capitalize">{c.provider_type}</p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusBadge status={c.is_active ? 'active' : 'inactive'} />
                  {testResult[c.credential_id] && (
                    <span className={`text-xs ${testResult[c.credential_id] === 'ok' ? 'text-success' : 'text-error'}`}>
                      {testResult[c.credential_id] === 'ok' ? '✓ Valid' : '✗ Failed'}
                    </span>
                  )}
                  <button onClick={() => handleTest(c.credential_id)} disabled={testing} className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors" title="Test">
                    <CheckCircle className="h-4 w-4" />
                  </button>
                  <button onClick={() => { if (confirm('Remove credential?')) remove(c.credential_id) }} className="text-error hover:opacity-70 transition-opacity" title="Remove">
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </ErrorBoundary>
    </div>
  )
}
