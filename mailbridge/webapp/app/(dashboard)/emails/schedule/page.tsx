'use client'

import { useState } from 'react'
import { useScheduledEmails, useCancelScheduled } from '@/lib/hooks/useEmails'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { EmptyState } from '@/components/shared/EmptyState'
import { Pagination } from '@/components/shared/Pagination'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatDateTime } from '@/lib/utils/formatDate'
import Link from 'next/link'
import { Clock, Plus, X } from 'lucide-react'

export default function ScheduledEmailsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useScheduledEmails(page)
  const { mutate: cancel } = useCancelScheduled()

  return (
    <div>
      <PageHeader
        title="Scheduled emails"
        description="Emails queued for future delivery"
        action={
          <Link href="/emails/send" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            <Plus className="h-4 w-4" /> Schedule email
          </Link>
        }
      />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <ErrorBoundary feature="Scheduled emails">
          {isLoading ? (
            <div className="p-5"><TableSkeleton rows={5} cols={4} /></div>
          ) : data?.scheduled.length === 0 ? (
            <EmptyState icon={Clock} title="No scheduled emails" description="Schedule an email to send it at a specific time" />
          ) : (
            <>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    {['To', 'Subject', 'Scheduled at', 'Status', ''].map((h, i) => (
                      <th key={i} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(data?.scheduled as Array<{ scheduled_id: string; to_email: string; subject: string; scheduled_at: string; status: string }>).map(e => (
                    <tr key={e.scheduled_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                      <td className="px-5 py-3 text-[var(--text)]">{e.to_email}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)] max-w-xs truncate">{e.subject}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)]">{formatDateTime(e.scheduled_at)}</td>
                      <td className="px-5 py-3"><StatusBadge status={e.status as 'pending'} /></td>
                      <td className="px-5 py-3">
                        {e.status === 'pending' && (
                          <button onClick={() => cancel(e.scheduled_id)} className="text-error hover:opacity-70 transition-opacity">
                            <X className="h-4 w-4" />
                          </button>
                        )}
                      </td>
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
