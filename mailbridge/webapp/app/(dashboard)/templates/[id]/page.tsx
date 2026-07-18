'use client'

import { use, useState } from 'react'
import { useTemplates, useUpdateTemplate } from '@/lib/hooks/useTemplates'
import { useForm } from 'react-hook-form'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/shared/PageHeader'
import { renderTemplate } from '@/lib/utils/renderTemplate'
import Link from 'next/link'
import { History } from 'lucide-react'

export default function EditTemplatePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const { data } = useTemplates()
  const template = data?.templates.find(t => t.template_id === id)
  const { mutateAsync: update } = useUpdateTemplate()
  const [preview, setPreview] = useState('')

  const { register, handleSubmit, watch, formState: { isSubmitting }, setError } = useForm({
    values: template ? { name: template.name, subject: template.subject, html: template.html, variables: '' } : undefined
  })

  const html = watch('html')
  const vars = watch('variables')

  function updatePreview() {
    try {
      const ctx = vars ? JSON.parse(vars) : {}
      setPreview(renderTemplate(html ?? '', ctx))
    } catch { setPreview(html ?? '') }
  }

  async function onSubmit(data: { name: string; subject: string; html: string }) {
    try {
      await update({ id, input: { name: data.name, subject: data.subject, html: data.html } })
      router.push('/templates')
    } catch (err: unknown) {
      setError('root', { message: err instanceof Error ? err.message : 'Update failed' })
    }
  }

  if (!template) return <p className="text-[var(--text-muted)]">Loading…</p>

  return (
    <div className="max-w-4xl">
      <PageHeader
        title={`Edit: ${template.name}`}
        description={`Version ${template.version}`}
        action={<Link href={`/templates/${id}/versions`} className="flex items-center gap-2 rounded-lg border border-[var(--border)] px-3 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--surface)] transition-colors"><History className="h-4 w-4" /> History</Link>}
      />
      <div className="grid grid-cols-2 gap-6">
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-base">
          <form onSubmit={handleSubmit(onSubmit as Parameters<typeof handleSubmit>[0])} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Name</label>
              <input {...register('name')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Subject</label>
              <input {...register('subject')} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">HTML body</label>
              <textarea {...register('html')} rows={10} className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono focus:outline-none focus:ring-2 focus:ring-accent/50 resize-y" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--text)] mb-1.5">Preview variables (JSON)</label>
              <input {...register('variables')} placeholder='{"name":"Alice"}' className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-sm text-[var(--text)] font-mono placeholder:text-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-accent/50" />
            </div>
            <button type="button" onClick={updatePreview} className="text-sm text-accent hover:underline">Update preview →</button>
            <div className="flex gap-3 pt-2">
              <button type="submit" disabled={isSubmitting} className="rounded-lg bg-accent px-5 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60 transition-colors">
                {isSubmitting ? 'Saving…' : 'Save changes'}
              </button>
              <button type="button" onClick={() => router.back()} className="rounded-lg border border-[var(--border)] px-5 py-2 text-sm text-[var(--text-muted)] hover:bg-[var(--bg)] transition-colors">Cancel</button>
            </div>
          </form>
        </div>
        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] shadow-base overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--border)]"><span className="text-sm font-medium text-[var(--text)]">Preview</span></div>
          <div className="p-5 prose prose-sm max-w-none text-[var(--text)]" dangerouslySetInnerHTML={{ __html: preview || '<p class="text-[var(--text-muted)]">Click "Update preview"</p>' }} />
        </div>
      </div>
    </div>
  )
}
