import { Sidebar } from '@/components/layout/Sidebar'
import { Topbar } from '@/components/layout/Topbar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--bg)]">
      <Sidebar />
      <Topbar />
      <main className="ml-56 pt-14 p-6 min-h-screen">
        {children}
      </main>
    </div>
  )
}
