'use client'

import { useState } from 'react'
import { useInboundLogs } from '@/lib/hooks/useEmails'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { EmptyState } from '@/components/shared/EmptyState'
import { Pagination } from '@/components/shared/Pagination'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatDateTime } from '@/lib/utils/formatDate'
import { Inbox } from 'lucide-react'

export default function IncomingLogsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useInboundLogs(page)

  return (
    <div>
      <PageHeader
        title="Incoming Logs"
        description="Metadata of emails received via IMAP or Push Notifications"
      />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <ErrorBoundary feature="Incoming Logs">
          {isLoading ? (
            <div className="p-5"><TableSkeleton rows={8} cols={4} /></div>
          ) : data?.logs.length === 0 ? (
            <EmptyState icon={Inbox} title="No incoming emails yet" description="Connect an account with IMAP or webhooks to start receiving emails" />
          ) : (
            <>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[var(--border)]">
                    {['From', 'Subject', 'Received at', 'Logged at'].map(h => (
                      <th key={h} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data?.logs.map(log => (
                    <tr key={log.log_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                      <td className="px-5 py-3 text-[var(--text)]">{log.from_address}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)] max-w-xs truncate">{log.subject || '—'}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)]">{log.received_at ? formatDateTime(log.received_at) : '—'}</td>
                      <td className="px-5 py-3 text-[var(--text-muted)]">{formatDateTime(log.created_at)}</td>
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
