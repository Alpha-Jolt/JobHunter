'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useTemplates, useDeleteTemplate } from '@/lib/hooks/useTemplates'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatDate } from '@/lib/utils/formatDate'
import { FileText, Plus, Pencil, Trash2, History } from 'lucide-react'

export default function TemplatesPage() {
  const { data, isLoading } = useTemplates()
  const { mutate: deleteTemplate } = useDeleteTemplate()
  const [deleting, setDeleting] = useState<string | null>(null)

  function handleDelete(id: string) {
    if (!confirm('Delete this template?')) return
    setDeleting(id)
    deleteTemplate(id, { onSettled: () => setDeleting(null) })
  }

  return (
    <div>
      <PageHeader
        title="Templates"
        description="Reusable email templates with variable support"
        action={
          <Link href="/templates/new" className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            <Plus className="h-4 w-4" /> New template
          </Link>
        }
      />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <ErrorBoundary feature="Templates">
          {isLoading ? (
            <div className="p-5"><TableSkeleton rows={5} cols={4} /></div>
          ) : data?.templates.length === 0 ? (
            <EmptyState icon={FileText} title="No templates" description="Create reusable email templates with Handlebars variables" action={<Link href="/templates/new" className="rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors">New template</Link>} />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {['Name', 'Subject', 'Version', 'Updated', ''].map((h, i) => (
                    <th key={i} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data?.templates.map(t => (
                  <tr key={t.template_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                    <td className="px-5 py-3 font-medium text-[var(--text)]">{t.name}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)] max-w-xs truncate">{t.subject}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">v{t.version}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{formatDate(t.updated_at)}</td>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-2 justify-end">
                        <Link href={`/templates/${t.template_id}/versions`} className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors" title="Version history">
                          <History className="h-4 w-4" />
                        </Link>
                        <Link href={`/templates/${t.template_id}`} className="text-[var(--text-muted)] hover:text-[var(--text)] transition-colors" title="Edit">
                          <Pencil className="h-4 w-4" />
                        </Link>
                        <button onClick={() => handleDelete(t.template_id)} disabled={deleting === t.template_id} className="text-error hover:opacity-70 disabled:opacity-40 transition-opacity" title="Delete">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </ErrorBoundary>
      </div>
    </div>
  )
}
