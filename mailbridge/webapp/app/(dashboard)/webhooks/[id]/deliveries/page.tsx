'use client'

import { use, useState } from 'react'
import { useWebhookDeliveries } from '@/lib/hooks/useWebhooks'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { Pagination } from '@/components/shared/Pagination'
import { formatDateTime } from '@/lib/utils/formatDate'

export default function WebhookDeliveriesPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [page, setPage] = useState(1)
  const { data, isLoading } = useWebhookDeliveries(id, page)

  return (
    <div>
      <PageHeader title="Delivery history" description="All delivery attempts for this webhook" />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        {isLoading ? (
          <div className="p-5"><TableSkeleton rows={6} cols={5} /></div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {['Event', 'Status', 'Attempts', 'Delivered at', 'Error'].map((h, i) => (
                    <th key={i} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data?.deliveries.map(d => (
                  <tr key={d.delivery_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                    <td className="px-5 py-3 font-mono text-xs text-[var(--text)]">{d.event}</td>
                    <td className="px-5 py-3"><StatusBadge status={d.status} /></td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{d.attempts}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{d.delivered_at ? formatDateTime(d.delivered_at) : '—'}</td>
                    <td className="px-5 py-3 text-error text-xs max-w-xs truncate">{d.last_error ?? '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div className="px-5 py-4 border-t border-[var(--border)]">
              <Pagination page={page} total={data?.total ?? 0} limit={20} onPageChange={setPage} />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
