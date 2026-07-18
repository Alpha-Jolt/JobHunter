import { cn } from '@/lib/utils/cn'

interface Props { rows?: number; cols?: number; className?: string }

export function TableSkeleton({ rows = 5, cols = 4, className }: Props) {
  return (
    <div className={cn('w-full animate-pulse', className)}>
      <div className="flex gap-4 mb-3">
        {Array.from({ length: cols }).map((_, i) => (
          <div key={i} className="h-4 bg-[var(--muted)] rounded flex-1 opacity-50" />
        ))}
      </div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-4 mb-3">
          {Array.from({ length: cols }).map((_, j) => (
            <div key={j} className="h-4 bg-[var(--muted)] rounded flex-1 opacity-30" />
          ))}
        </div>
      ))}
    </div>
  )
}
