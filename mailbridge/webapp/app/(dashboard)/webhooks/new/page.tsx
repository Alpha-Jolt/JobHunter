'use client'

import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useCreateWebhook } from '@/lib/hooks/useWebhooks'
import { PageHeader } from '@/components/shared/PageHeader'
import type { WebhookEvent } from '@/lib/types/api'

const EVENTS: WebhookEvent[] = ['email.sent', 'email.failed', 'email.bounced']

const schema = z.object({
  url: z.string().url('Must be a valid URL'),
  events: z.array(z.string()).min(1, 'Select at least one event'),
  secret: z.string().min(8, 'Min 8 characters')
})
type FormData = z.infer<typeof schema>

export default function NewWebhookPage() {
  const router = useRouter()
  const { mutateAsync: create } = useCreateWebhook()
  const [created, setCreated] = useState<{ secret: string } | null>(null)
  const { register, control, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { events: ['email.sent', 'email.failed'] }
  })

  async function onSubmit(data: FormData) {
    try {
      const res = await create({ url: data.url, events: data.events as WebhookEvent[], secret: data.secret })
      setCreated({ secret: res.secret })
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Create failed' })
    }
  }

  if (created) return (
    <div className="max-w-lg">
      <div className="rounded-xl border border-success/30 bg-success/5 p-6 shadow-base">
        <h2 className="font-semibold text-[var(--text)] mb-2">Webhook created</h2>
        <p className="text-sm text-[var(--text-muted)] mb-4">Save your signing secret — it will not be shown again.</p>
        <div className="rounded-lg bg-[var(--bg)] border border-[var(--border)] px-4 py-3 font-mono text-sm text-[var(--text)] break-all">{created.secret}</div>
        <button onClick={() => router.push('/webhooks')} className="mt-4 rounded-lg bg-accent px-5 py-2 text-sm text-white hover:bg-accent-hover transition-colors">Done</button>
      </div>
    </div>
  )

  return (
    <div className="max-w-lg">
      <PageHeader title="New webhook" description="Register a URL to receive email events" />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">URL</label>
            <input {...register('url')} placeholder="https://myapp.com/webhooks/mail" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            {errors.url && <p className="mt-1 text-xs text-error">{errors.url.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-2">Events</label>
            <Controller
              control={control}
              name="events"
              render={({ field }) => (
                <div className="space-y-2">
                  {EVENTS.map(e => (
                    <label key={e} className="flex items-center gap-2 text-sm text-[var(--text)]">
                      <input
                        type="checkbox"
                        checked={field.value.includes(e)}
                        onChange={ev => field.onChange(ev.target.checked ? [...field.value, e] : field.value.filter(v => v !== e))}
                        className="rounded"
                      />
                      {e}
                    </label>
                  ))}
                </div>
              )}
            />
            {errors.events && <p className="mt-1 text-xs text-error">{errors.events.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Signing secret</label>
            <input {...register('secret')} type="password" placeholder="Min 8 characters" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            {errors.secret && <p className="mt-1 text-xs text-error">{errors.secret.message}</p>}
          </div>

          {errors.root && <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
              {isSubmitting ? 'Creating…' : 'Create webhook'}
            </button>
            <button type="button" onClick={() => router.back()} className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--bg)] transition-colors">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  )
}
