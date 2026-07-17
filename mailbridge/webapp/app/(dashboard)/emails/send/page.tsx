'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useSendEmail } from '@/lib/hooks/useEmails'
import { useCredentials } from '@/lib/hooks/useCredentials'
import { useTemplates } from '@/lib/hooks/useTemplates'
import { PageHeader } from '@/components/shared/PageHeader'

const schema = z.object({
  credential_id: z.string().min(1, 'Select a credential'),
  to_email: z.string().email('Invalid email'),
  subject: z.string().optional(),
  html: z.string().optional(),
  template_id: z.string().optional(),
  variables: z.string().optional()
})
type FormData = z.infer<typeof schema>

export default function SendEmailPage() {
  const router = useRouter()
  const { mutateAsync: send } = useSendEmail()
  const { data: creds } = useCredentials()
  const { data: templates } = useTemplates()

  const { register, handleSubmit, watch, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema)
  })

  const templateId = watch('template_id')

  async function onSubmit(data: FormData) {
    try {
      let variables: Record<string, unknown> = {}
      if (data.variables) {
        try { variables = JSON.parse(data.variables) } catch { setError('variables', { message: 'Invalid JSON' }); return }
      }
      await send({ ...data, variables, template_id: data.template_id || undefined, subject: data.subject || undefined, html: data.html || undefined })
      router.push('/emails')
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Send failed' })
    }
  }

  return (
    <div className="max-w-2xl">
      <PageHeader title="Send email" description="Send a single email" />

      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Credential</label>
            <select {...register('credential_id')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50">
              <option value="">Select credential…</option>
              {creds?.credentials.map(c => (
                <option key={c.credential_id} value={c.credential_id}>{c.from_email} ({c.provider_type})</option>
              ))}
            </select>
            {errors.credential_id && <p className="mt-1 text-xs text-error">{errors.credential_id.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">To</label>
            <input {...register('to_email')} type="email" placeholder="recipient@example.com" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            {errors.to_email && <p className="mt-1 text-xs text-error">{errors.to_email.message}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Template (optional)</label>
            <select {...register('template_id')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50">
              <option value="">No template — use subject/html below</option>
              {templates?.templates.map(t => (
                <option key={t.template_id} value={t.template_id}>{t.name} (v{t.version})</option>
              ))}
            </select>
          </div>

          {!templateId && (
            <>
              <div>
                <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Subject</label>
                <input {...register('subject')} placeholder="Hello {{name}}" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text)] mb-1.5">HTML body</label>
                <textarea {...register('html')} rows={6} placeholder="<p>Hello {{name}}</p>" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 resize-y" />
              </div>
            </>
          )}

          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Variables (JSON)</label>
            <textarea {...register('variables')} rows={3} placeholder='{"name": "Alice"}' className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 resize-y" />
            {errors.variables && <p className="mt-1 text-xs text-error">{errors.variables.message}</p>}
          </div>

          {errors.root && <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>}

          <div className="flex gap-3 pt-2">
            <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
              {isSubmitting ? 'Sending…' : 'Send email'}
            </button>
            <button type="button" onClick={() => router.back()} className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--bg)] transition-colors">
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
