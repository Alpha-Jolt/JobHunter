import { ChevronLeft, ChevronRight } from 'lucide-react'
import { cn } from '@/lib/utils/cn'

interface Props {
  page: number
  total: number
  limit: number
  onPageChange: (page: number) => void
}

export function Pagination({ page, total, limit, onPageChange }: Props) {
  const totalPages = Math.ceil(total / limit)
  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between text-sm text-[var(--text-muted)]">
      <span>{((page - 1) * limit) + 1}–{Math.min(page * limit, total)} of {total}</span>
      <div className="flex gap-1">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          className={cn(
            'rounded-lg p-1.5 hover:bg-[var(--muted)]/30 transition-colors',
            page === 1 && 'opacity-40 cursor-not-allowed'
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
        <span className="px-3 py-1">{page} / {totalPages}</span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          className={cn(
            'rounded-lg p-1.5 hover:bg-[var(--muted)]/30 transition-colors',
            page === totalPages && 'opacity-40 cursor-not-allowed'
          )}
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
