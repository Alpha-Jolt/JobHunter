'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useWebhooks, useDeleteWebhook, useUpdateWebhook, useTestWebhook } from '@/lib/hooks/useWebhooks'
import { PageHeader } from '@/components/shared/PageHeader'
import { CardSkeleton } from '@/components/shared/CardSkeleton'
import { EmptyState } from '@/components/shared/EmptyState'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { Webhook, Plus, Trash2, Play, ToggleLeft, ToggleRight, History } from 'lucide-react'

export default function WebhooksPage() {
  const { data, isLoading } = useWebhooks()
  const { mutate: remove } = useDeleteWebhook()
  const { mutate: update } = useUpdateWebhook()
  const { mutate: test } = useTestWebhook()
  const [testMsg, setTestMsg] = useState<Record<string, string>>({})

  function handleTest(id: string) {
    test(id, {
      onSuccess: () => setTestMsg(p => ({ ...p, [id]: 'Delivered' })),
      onError: () => setTestMsg(p => ({ ...p, [id]: 'Failed' }))
    })
  }

  return (
    <div>
      <PageHeader
        title="Webhooks"
        description="Receive events when emails are sent or fail"
        action={
          <Link href="/webhooks/new" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            <Plus className="h-4 w-4" /> New webhook
          </Link>
        }
      />

      <ErrorBoundary feature="Webhooks">
        {isLoading ? (
          <CardSkeleton count={3} />
        ) : data?.webhooks.length === 0 ? (
          <EmptyState icon={Webhook} title="No webhooks" description="Register a URL to receive email delivery events" action={<Link href="/webhooks/new" className="rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors">New webhook</Link>} />
        ) : (
          <div className="grid gap-3">
            {data?.webhooks.map(w => (
              <div key={w.webhook_id} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] px-5 py-4 shadow-base">
                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-sm text-[var(--text)] truncate">{w.url}</p>
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {w.events.map(e => (
                        <span key={e} className="rounded-full bg-accent/10 px-2 py-0.5 text-xs text-accent">{e}</span>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4 shrink-0">
                    <StatusBadge status={w.is_active ? 'active' : 'inactive'} />
                    {testMsg[w.webhook_id] && <span className="text-xs text-[var(--text-muted)]">{testMsg[w.webhook_id]}</span>}
                    <button onClick={() => handleTest(w.webhook_id)} title="Test" className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"><Play className="h-4 w-4" /></button>
                    <button onClick={() => update({ id: w.webhook_id, input: { is_active: !w.is_active } })} title="Toggle" className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors">
                      {w.is_active ? <ToggleRight className="h-4 w-4 text-success" /> : <ToggleLeft className="h-4 w-4" />}
                    </button>
                    <Link href={`/webhooks/${w.webhook_id}/deliveries`} title="Deliveries" className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors"><History className="h-4 w-4" /></Link>
                    <button onClick={() => { if (confirm('Delete webhook?')) remove(w.webhook_id) }} className="text-error hover:opacity-70 transition-opacity"><Trash2 className="h-4 w-4" /></button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </ErrorBoundary>
    </div>
  )
}
