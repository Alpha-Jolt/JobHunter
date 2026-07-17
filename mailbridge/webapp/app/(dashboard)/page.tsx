'use client'

import { useEmails, useEmailStats } from '@/lib/hooks/useEmails'
import { useCredentials } from '@/lib/hooks/useCredentials'
import { useTemplates } from '@/lib/hooks/useTemplates'
import { PageHeader } from '@/components/shared/PageHeader'
import { CardSkeleton } from '@/components/shared/CardSkeleton'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatRelative } from '@/lib/utils/formatDate'
import { Mail, Key, FileText, Activity } from 'lucide-react'

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: React.ElementType }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-base">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-[var(--text-muted)]">{label}</span>
        <Icon className="h-4 w-4 text-accent" />
      </div>
      <p className="text-3xl font-semibold text-[var(--text)]">{value}</p>
    </div>
  )
}

function EmailStatusCard({ sent, failed, queued }: { sent: number | string, failed: number | string, queued: number | string }) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-base">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-[var(--text-muted)]">Total Status</span>
        <Activity className="h-4 w-4 text-accent" />
      </div>
      <div className="flex justify-between items-end mt-2">
        <div className="flex flex-col">
          <span className="text-2xl font-semibold text-success">{sent}</span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)] mt-1">Sent</span>
        </div>
        <div className="flex flex-col">
          <span className="text-2xl font-semibold text-error">{failed}</span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)] mt-1">Failed</span>
        </div>
        <div className="flex flex-col">
          <span className="text-2xl font-semibold text-warning">{queued}</span>
          <span className="text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)] mt-1">Queued</span>
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: emailsData, isLoading: emailsLoading } = useEmails(1, 5)
  const { data: statsData } = useEmailStats()
  const { data: credsData } = useCredentials()
  const { data: templatesData } = useTemplates()

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your workspace" />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Emails today" value={statsData?.stats?.today ?? '—'} icon={Mail} />
        <StatCard label="Credentials" value={credsData?.credentials.length ?? '—'} icon={Key} />
        <StatCard label="Templates" value={templatesData?.templates.length ?? '—'} icon={FileText} />
        <EmailStatusCard 
          sent={statsData?.stats?.sent ?? '—'} 
          failed={statsData?.stats?.failed ?? '—'} 
          queued={statsData?.stats?.queued ?? '—'} 
        />
      </div>

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <div className="px-5 py-4 border-b border-[var(--border)]">
          <h2 className="font-medium text-[var(--text)]">Recent emails</h2>
        </div>
        <ErrorBoundary feature="Recent emails">
          {emailsLoading ? (
            <div className="p-5"><CardSkeleton count={3} /></div>
          ) : emailsData?.emails.length === 0 ? (
            <p className="p-8 text-center text-sm text-[var(--text-muted)]">No emails sent yet</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {['To', 'Subject', 'Status', 'Sent'].map(h => (
                    <th key={h} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {emailsData?.emails.map(e => (
                  <tr key={e.email_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                    <td className="px-5 py-3 text-[var(--text)]">{e.to_email}</td>
                    <td className="px-5 py-3 text-[var(--text-muted)] max-w-xs truncate">{e.subject}</td>
                    <td className="px-5 py-3"><StatusBadge status={e.status} /></td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{e.sent_at ? formatRelative(e.sent_at) : '—'}</td>
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
