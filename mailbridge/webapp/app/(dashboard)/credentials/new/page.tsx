'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useAddSmtp } from '@/lib/hooks/useCredentials'
import { PageHeader } from '@/components/shared/PageHeader'

const schema = z.object({
  from_email: z.string().email('Invalid email'),
  host: z.string().min(1, 'Required'),
  port: z.coerce.number().int().min(1).max(65535),
  secure: z.boolean().default(false),
  user: z.string().min(1, 'Required'),
  pass: z.string().min(1, 'Required'),
  imap_host: z.string().optional().or(z.literal('')),
  imap_port: z.coerce.number().int().min(1).max(65535).optional().or(z.literal('')),
  imap_secure: z.boolean().optional(),
  imap_sync_mode: z.enum(['idle', 'polling']).optional().or(z.literal('')),
  imap_poll_interval: z.coerce.number().int().min(1).optional().or(z.literal(''))
})
type FormData = z.infer<typeof schema>

export default function NewCredentialPage() {
  const router = useRouter()
  const { mutateAsync: addSmtp } = useAddSmtp()
  const { register, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { port: 587, secure: false }
  })

  async function onSubmit(data: FormData) {
    try {
      const payload = { ...data }
      if (!payload.imap_host) {
        delete payload.imap_host
        delete payload.imap_port
        delete payload.imap_secure
        delete payload.imap_sync_mode
        delete payload.imap_poll_interval
      } else {
        if (payload.imap_sync_mode === '') delete payload.imap_sync_mode
      }
      await addSmtp(payload)
      router.push('/credentials')
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Failed to add credential' })
    }
  }

  return (
    <div className="max-w-lg">
      <PageHeader title="Add SMTP credential" description="Connect a custom SMTP server" />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {[
            { name: 'from_email' as const, label: 'From email', type: 'email', placeholder: 'you@example.com' },
            { name: 'host' as const, label: 'SMTP host', type: 'text', placeholder: 'smtp.example.com' },
            { name: 'port' as const, label: 'Port', type: 'number', placeholder: '587' },
            { name: 'user' as const, label: 'Username', type: 'text', placeholder: 'you@example.com' },
            { name: 'pass' as const, label: 'Password', type: 'password', placeholder: '••••••••' }
          ].map(f => (
            <div key={f.name}>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">{f.label}</label>
              <input {...register(f.name)} type={f.type} placeholder={f.placeholder} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              {errors[f.name] && <p className="mt-1 text-xs text-error">{errors[f.name]?.message}</p>}
            </div>
          ))}

          <label className="flex items-center gap-2 text-sm text-[var(--text)]">
            <input {...register('secure')} type="checkbox" className="rounded" />
            Use TLS (port 465)
          </label>

          <hr className="my-6 border-[var(--border)]" />
          <h3 className="text-sm font-medium text-[var(--text)]">Inbound (IMAP) Configuration (Optional)</h3>
          <p className="text-xs text-[var(--text-muted)] mb-4">Required if you want to fetch incoming emails via IMAP.</p>
          
          {[
            { name: 'imap_host' as const, label: 'IMAP host', type: 'text', placeholder: 'imap.example.com' },
            { name: 'imap_port' as const, label: 'IMAP Port', type: 'number', placeholder: '993' }
          ].map(f => (
            <div key={f.name}>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">{f.label}</label>
              <input {...register(f.name)} type={f.type} placeholder={f.placeholder} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              {errors[f.name] && <p className="mt-1 text-xs text-error">{errors[f.name]?.message}</p>}
            </div>
          ))}

          <label className="flex items-center gap-2 text-sm text-[var(--text)]">
            <input {...register('imap_secure')} type="checkbox" className="rounded" />
            Use TLS for IMAP (port 993)
          </label>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Sync Mode</label>
            <select {...register('imap_sync_mode')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50">
              <option value="">Select mode...</option>
              <option value="idle">Persistent Connection (IDLE) - Realtime, uses more resources</option>
              <option value="polling">Polling - Checks periodically</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Poll Interval (minutes)</label>
            <input {...register('imap_poll_interval')} type="number" placeholder="5" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
          </div>

          {errors.root && <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
              {isSubmitting ? 'Adding…' : 'Add credential'}
            </button>
            <button type="button" onClick={() => router.back()} className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--bg)] transition-colors">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
