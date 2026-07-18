'use client'

import { useAuth } from '@/lib/hooks/useAuth'
import { PageHeader } from '@/components/shared/PageHeader'
import { ThemeToggle } from '@/components/layout/ThemeToggle'

export default function SettingsPage() {
  const { user } = useAuth()

  return (
    <div className="max-w-2xl">
      <PageHeader title="Settings" description="Workspace and account preferences" />

      <div className="space-y-4">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
          <h2 className="font-medium text-[var(--text)] mb-4">Account</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-[var(--text-muted)]">Email</span>
              <span className="text-[var(--text)]">{user?.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--text-muted)]">Role</span>
              <span className="text-[var(--text)] capitalize">{user?.role}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--text-muted)]">Workspace tier</span>
              <span className="text-[var(--text)] capitalize">{user?.tier}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--text-muted)]">Workspace ID</span>
              <span className="text-[var(--text)] font-mono text-xs">{user?.workspace_id}</span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
          <h2 className="font-medium text-[var(--text)] mb-4">Appearance</h2>
          <div className="flex items-center justify-between">
            <span className="text-sm text-[var(--text-muted)]">Theme</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </div>
  )
}
