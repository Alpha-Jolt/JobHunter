'use client'

import { useState } from 'react'
import { useAdminUsers, useInviteUser, useChangeRole, useRemoveUser } from '@/lib/hooks/useAdmin'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PageHeader } from '@/components/shared/PageHeader'
import { TableSkeleton } from '@/components/shared/TableSkeleton'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorBoundary } from '@/components/shared/ErrorBoundary'
import { formatDate } from '@/lib/utils/formatDate'
import { Users, Trash2 } from 'lucide-react'
import type { FlatRole } from '@/lib/types/api'

const schema = z.object({
  email: z.string().email('Invalid email'),
  role: z.enum(['owner', 'member'])
})
type FormData = z.infer<typeof schema>

export default function AdminPage() {
  const { data, isLoading } = useAdminUsers()
  const { mutateAsync: invite } = useInviteUser()
  const { mutate: changeRole } = useChangeRole()
  const { mutate: removeUser } = useRemoveUser()
  const [showInvite, setShowInvite] = useState(false)

  const { register, handleSubmit, reset, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { role: 'member' }
  })

  async function onInvite(data: FormData) {
    try {
      await invite({ email: data.email, role: data.role as FlatRole })
      reset()
      setShowInvite(false)
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Invite failed' })
    }
  }

  return (
    <div>
      <PageHeader
        title="Team"
        description="Manage workspace members"
        action={
          <button onClick={() => setShowInvite(v => !v)} className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover transition-colors">
            Invite member
          </button>
        }
      />

      {showInvite && (
        <div className="mb-6 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-base">
          <form onSubmit={handleSubmit(onInvite)} className="flex items-end gap-3">
            <div className="flex-1">
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Email</label>
              <input {...register('email')} type="email" placeholder="member@example.com" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              {errors.email && <p className="mt-1 text-xs text-error">{errors.email.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Role</label>
              <select {...register('role')} className="rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50">
                <option value="member">Member</option>
                <option value="owner">Owner</option>
              </select>
            </div>
            <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
              {isSubmitting ? 'Inviting…' : 'Invite'}
            </button>
          </form>
          {errors.root && <p className="mt-2 text-sm text-error">{errors.root.message}</p>}
        </div>
      )}

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base">
        <ErrorBoundary feature="Team">
          {isLoading ? (
            <div className="p-5"><TableSkeleton rows={4} cols={4} /></div>
          ) : data?.users.length === 0 ? (
            <EmptyState icon={Users} title="No team members" description="Invite members to collaborate" />
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)]">
                  {['Email', 'Role', 'Joined', ''].map((h, i) => (
                    <th key={i} className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data?.users.map(u => (
                  <tr key={u.user_id} className="border-b border-[var(--border)] last:border-0 hover:bg-[var(--bg)] transition-colors">
                    <td className="px-5 py-3 text-[var(--text)]">{u.email}</td>
                    <td className="px-5 py-3">
                      <select
                        value={u.role}
                        onChange={e => changeRole({ userId: u.user_id, role: e.target.value as FlatRole })}
                        className="rounded-lg border border-[var(--border)] bg-[var(--bg)] px-2 py-1 text-xs text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50"
                      >
                        <option value="member">Member</option>
                        <option value="owner">Owner</option>
                      </select>
                    </td>
                    <td className="px-5 py-3 text-[var(--text-muted)]">{formatDate(u.created_at)}</td>
                    <td className="px-5 py-3">
                      <button onClick={() => { if (confirm('Remove member?')) removeUser(u.user_id) }} className="text-error hover:opacity-70 transition-opacity">
                        <Trash2 className="h-4 w-4" />
                      </button>
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
