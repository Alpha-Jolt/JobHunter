'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useEmails } from '@/lib/hooks/useEmails'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { EmptyState } from '@/components/shared/EmptyState'
import { Pagination } from '@/components/shared/Pagination'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatDateTime } from '@/lib/utils/formatDate'
import { Mail, Plus } from 'lucide-react'

export default function EmailsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useEmails(page)

  return (
    <div>
      <PageHeader
        title="Emails"
        description="All sent and queued emails"
        action={
          <Link href="/emails/send" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            <Plus className="h-4 w-4" /> Send email
          </Link>
        }
      />

      <div className="mb-4 flex gap-2">
        <Link href="/emails/batch" className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">Batch send</Link>
        <Link href="/emails/schedule" className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors">Scheduled</Link>
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <ErrorBoundary feature="Emails">
          {isLoading ? (
            <div className="p-5"><TableSkeleton rows={8} cols={5} /></div>
          ) : data?.emails.length === 0 ? (
            <EmptyState icon={Mail} title="No emails yet" description="Send your first email to get started" action={<Link href="/emails/send" className="rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors">Send email</Link>} />
          ) : (
            <>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    {['To', 'Subject', 'Status', 'Provider ID', 'Sent at'].map(h => (
                      <th key={h} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data?.emails.map(e => (
                    <tr key={e.email_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors cursor-pointer">
                      <td className="px-5 py-3 text-[var(--text)]">{e.to_email}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)] max-w-xs truncate">{e.subject}</td>
                      <td className="px-5 py-3"><StatusBadge status={e.status} /></td>
                      <td className="px-5 py-3 text-[var(--text-muted)] font-mono text-xs">{e.provider_message_id ?? '—'}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)]">{e.sent_at ? formatDateTime(e.sent_at) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="px-5 py-4 border-t border-[var(--border)]">
                <Pagination page={page} total={data?.total ?? 0} limit={20} onPageChange={setPage} />
              </div>
            </>
          )}
        </ErrorBoundary>
      </div>
    </div>
  )
}
