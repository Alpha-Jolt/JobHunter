'use client'

import { use, useState } from 'react'
import { useTemplateVersions, useRollbackTemplate } from '@/lib/hooks/useTemplates'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { Pagination } from '@/components/shared/Pagination'
import { formatDateTime } from '@/lib/utils/formatDate'
import { RotateCcw } from 'lucide-react'

export default function VersionHistoryPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const [page, setPage] = useState(1)
  const { data, isLoading } = useTemplateVersions(id, page)
  const { mutate: rollback, isPending } = useRollbackTemplate()

  function handleRollback(version: number) {
    if (!confirm(`Rollback to version ${version}?`)) return
    rollback({ id, version })
  }

  return (
    <div className="max-w-3xl">
      <PageHeader title="Version history" description="All saved versions of this template" />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        {isLoading ? (
          <div className="p-5"><TableSkeleton rows={5} cols={4} /></div>
        ) : (
          <>
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {['Version', 'Name', 'Snapshotted at', ''].map((h, i) => (
                    <th key={i} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data?.versions.map(v => (
                  <tr key={v.version_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                    <td className="px-5 py-3 font-mono text-[var(--text)]">v{v.version}</td>
                    <td className="px-5 py-3 text-[var(--text)]">{v.name}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{formatDateTime(v.snapshotted_at)}</td>
                    <td className="px-5 py-3">
                      <button onClick={() => handleRollback(v.version)} disabled={isPending} className="flex items-center gap-1.5 text-xs text-accent hover:underline disabled:opacity-50">
                        <RotateCcw className="h-3.5 w-3.5" /> Rollback
                      </button>
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
      </div>
    </div>
  )
}
