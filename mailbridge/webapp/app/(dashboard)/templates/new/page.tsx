'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { useCreateTemplate } from '@/lib/hooks/useTemplates'
import { PageHeader } from '@/components/shared/PageHeader'
import { renderTemplate } from '@/lib/utils/renderTemplate'

const schema = z.object({
  name: z.string().min(1, 'Required'),
  subject: z.string().min(1, 'Required'),
  html: z.string().min(1, 'Required'),
  variables: z.string().optional()
})
type FormData = z.infer<typeof schema>

export default function NewTemplatePage() {
  const router = useRouter()
  const { mutateAsync: create } = useCreateTemplate()
  const [preview, setPreview] = useState('')
  const { register, handleSubmit, watch, formState: { errors, isSubmitting }, setError } = useForm<FormData>({
    resolver: zodResolver(schema)
  })

  const html = watch('html')
  const vars = watch('variables')

  function updatePreview() {
    try {
      const context = vars ? JSON.parse(vars) : {}
      setPreview(renderTemplate(html ?? '', context))
    } catch { setPreview(html ?? '') }
  }

  async function onSubmit(data: FormData) {
    try {
      await create({ name: data.name, subject: data.subject, html: data.html })
      router.push('/templates')
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Create failed' })
    }
  }

  return (
    <div className="max-w-4xl">
      <PageHeader title="New template" description="Create a reusable email template" />
      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Name</label>
              <input {...register('name')} placeholder="Welcome email" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              {errors.name && <p className="mt-1 text-xs text-error">{errors.name.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Subject</label>
              <input {...register('subject')} placeholder="Welcome {{name}}!" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
              {errors.subject && <p className="mt-1 text-xs text-error">{errors.subject.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">HTML body</label>
              <textarea {...register('html')} rows={10} placeholder="<p>Hello {{name}}</p>" className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50 resize-y" />
              {errors.html && <p className="mt-1 text-xs text-error">{errors.html.message}</p>}
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Preview variables (JSON)</label>
              <input {...register('variables')} placeholder='{"name":"Alice"}' className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            </div>
            <button type="button" onClick={updatePreview} className="text-sm text-accent hover:underline">Update preview →</button>
            {errors.root && <p className="rounded-lg bg-error/10 px-3 py-2 text-sm text-error">{errors.root.message}</p>}
            <div className="flex gap-3 pt-2">
              <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
                {isSubmitting ? 'Creating…' : 'Create template'}
              </button>
              <button type="button" onClick={() => router.back()} className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--bg)] transition-colors">Cancel</button>
            </div>
          </form>
        </div>

        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--border)]">
            <span className="text-sm font-medium text-[var(--text)]">Preview</span>
          </div>
          <div className="p-5 prose prose-sm max-w-none text-[var(--text)]" dangerouslySetInnerHTML={{ __html: preview || '<p class="text-[var(--text-muted)]">Click "Update preview" to see rendered output</p>' }} />
        </div>
      </div>
    </div>
  )
}
