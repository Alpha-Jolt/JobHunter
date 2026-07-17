import { cn } from '@/lib/utils/cn'

interface Props { count?: number; className?: string }

export function CardSkeleton({ count = 3, className }: Props) {
  return (
    <div className={cn('grid gap-4', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
          <div className="h-4 w-1/3 bg-[var(--muted)] rounded mb-3 opacity-50" />
          <div className="h-3 w-2/3 bg-[var(--muted)] rounded opacity-30" />
        </div>
      ))}
    </div>
  )
}
