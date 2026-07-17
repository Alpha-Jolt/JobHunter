'use client'

import { Component, type ReactNode } from 'react'
import { AlertCircle } from 'lucide-react'

interface Props { children: ReactNode; feature?: string }
interface State { hasError: boolean; message: string }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' }

  static getDerivedStateFromError(err: Error): State {
    return { hasError: true, message: err.message }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
          <AlertCircle className="h-8 w-8 text-error" />
          <p className="font-medium text-[var(--text)]">
            {this.props.feature ? `${this.props.feature} failed to load` : 'Something went wrong'}
          </p>
          <p className="text-sm text-[var(--text-muted)]">{this.state.message}</p>
          <button
            onClick={() => this.setState({ hasError: false, message: '' })}
            className="mt-2 rounded-lg bg-accent px-4 py-2 text-sm text-white hover:bg-accent-hover transition-colors"
          >
            Try again
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
