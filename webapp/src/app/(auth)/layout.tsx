import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = { title: "JobHunter — Sign in" };

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="auth-shell">
      <div className="w-full max-w-[400px]">
        <div className="text-center mb-8">
          <Link href="/" className="inline-block font-brand text-[2rem] font-semibold tracking-wide leading-none">
            <span className="text-brand-charcoal dark:text-paper">Job</span>
            <span className="text-ember">Hunter</span>
          </Link>
          <p className="mt-3 text-sm text-foreground-muted">Apply smart, not just fast.</p>
        </div>
        {children}
      </div>
    </div>
  );
}
