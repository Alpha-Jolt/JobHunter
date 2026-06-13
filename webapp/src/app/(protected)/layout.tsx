import { Navbar } from "@/shared/layout/Navbar";
import { AuthGuard } from "@/features/auth/AuthGuard";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <Navbar />
      <main className="pt-14 min-h-screen bg-background">
        <div className="max-w-7xl mx-auto px-4 py-6">{children}</div>
      </main>
    </AuthGuard>
  );
}
