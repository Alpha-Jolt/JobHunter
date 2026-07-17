'use client'

import { useState } from 'react'
import { useForm, useFieldArray } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useSendBatch } from '@/lib/hooks/useEmails'
import { useCredentials } from '@/lib/hooks/useCredentials'
import { PageHeader } from '@/components/shared/PageHeader'
import { Plus, Trash2 } from 'lucide-react'

const rowSchema = z.object({
  to_email: z.string().email('Invalid email'),
  subject: z.string().min(1, 'Required'),
  html: z.string().min(1, 'Required'),
  variables: z.string().optional()
})

const schema = z.object({
  credential_id: z.string().min(1, 'Select a credential'),
  emails: z.array(rowSchema).min(1)
})
type FormData = z.infer<typeof schema>

export default function BatchSendPage() {
  const router = useRouter()
  const { mutateAsync: sendBatch } = useSendBatch()
  const { data: creds } = useCredentials()
  const [result, setResult] = useState<{ queued: number } | null>(null)

  const { register, control, handleSubmit, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { emails: [{ to_email: '', subject: '', html: '', variables: '' }] }
  })
  const { fields, append, remove } = useFieldArray({ control, name: 'emails' })

  async function onSubmit(data: FormData) {
    try {
      const emails = data.emails.map(e => ({
        credential_id: data.credential_id,
        to_email: e.to_email,
        subject: e.subject,
        html: e.html,
        variables: e.variables ? JSON.parse(e.variables) : {}
      }))
      const res = await sendBatch(emails)
      setResult({ queued: res.queued })
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Batch send failed' })
    }
  }

  if (result) return (
    <div className="max-w-lg">
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center shadow-base">
        <p className="text-2xl font-semibold text-[var(--text)] mb-2">{result.queued} emails queued</p>
        <p className="text-sm text-[var(--text-muted)] mb-6">They will be processed shortly</p>
        <button onClick={() => router.push('/emails')} className="rounded-lg bg-accent px-5 py-2 text-sm text-white hover:bg-accent-hover transition-colors">View emails</button>
      </div>
    </div>
  )

  return (
    <div className="max-w-3xl">
      <PageHeader title="Batch send" description="Send multiple emails at once" />
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Credential (applies to all)</label>
            <select {...register('credential_id')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50">
              <option value="">Select credential…</option>
              {creds?.credentials.map(c => <option key={c.credential_id} value={c.credential_id}>{c.from_email} ({c.provider_type})</option>)}
            </select>
          </div>

          <div className="space-y-3">
            {fields.map((field, i) => (
              <div key={field.id} className="rounded-lg border border-[var(--border)] p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-[var(--text-muted)]">Email {i + 1}</span>
                  {fields.length > 1 && <button type="button" onClick={() => remove(i)} className="text-error hover:opacity-70"><Trash2 className="h-4 w-4" /></button>}
                </div>
                <input {...register(`emails.${i}.to_email`)} placeholder="to@example.com" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
                <input {...register(`emails.${i}.subject`)} placeholder="Subject" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
                <textarea {...register(`emails.${i}.html`)} rows={3} placeholder="<p>HTML body</p>" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 resize-y" />
              </div>
            ))}
          </div>

          <button type="button" onClick={() => append({ to_email: '', subject: '', html: '', variables: '' })} className="flex items-center gap-2 text-sm text-accent hover:underline">
            <Plus className="h-4 w-4" /> Add email
          </button>

          {errors.root && <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>}

          <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
            {isSubmitting ? 'Sending…' : `Send ${fields.length} email${fields.length > 1 ? 's' : ''}`}
          </button>
        </form>
      </div>
    </div>
  )
}
