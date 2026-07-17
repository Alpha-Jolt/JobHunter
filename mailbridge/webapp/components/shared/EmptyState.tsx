import { type LucideIcon } from 'lucide-react'

interface Props {
  title: string
  description?: string
  icon?: LucideIcon
  action?: React.ReactNode
}

export function EmptyState({ title, description, icon: Icon, action }: Props) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-12 text-center">
      {Icon && <Icon className="h-10 w-10 text-[var(--text-muted)]" />}
      <p className="font-medium text-[var(--text)]">{title}</p>
      {description && <p className="text-sm text-[var(--text-muted)] max-w-sm">{description}</p>}
      {action && <div className="mt-2">{action}</div>}
    </div>
  )
}
