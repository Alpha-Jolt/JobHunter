import { cn } from '@/lib/utils/cn'
import type { EmailStatus, WebhookDeliveryStatus, ScheduledEmailStatus } from '@/lib/types/api'

type Status = EmailStatus | WebhookDeliveryStatus | ScheduledEmailStatus | 'active' | 'inactive'

const styles: Record<string, string> = {
  sent:      'bg-success/10 text-success',
  delivered: 'bg-success/10 text-success',
  active:    'bg-success/10 text-success',
  queued:    'bg-warning/10 text-warning',
  pending:   'bg-warning/10 text-warning',
  failed:    'bg-error/10 text-error',
  bounced:   'bg-error/10 text-error',
  cancelled: 'bg-[var(--muted)]/30 text-[var(--text-muted)]',
  inactive:  'bg-[var(--muted)]/30 text-[var(--text-muted)]'
}

export function StatusBadge({ status, className }: { status: Status; className?: string }) {
  return (
    <span className={cn(
      'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize',
      styles[status] ?? 'bg-[var(--muted)]/30 text-[var(--text-muted)]',
      className
    )}>
      {status}
    </span>
  )
}
