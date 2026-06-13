import type { Metadata } from "next";

export const metadata: Metadata = { title: "JobHunter — Sign in" };

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background-subtle px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">
            <span className="text-brand-charcoal dark:text-foreground">Job</span>
            <span className="text-brand-orange">Hunter</span>
          </h1>
        </div>
        {children}
      </div>
    </div>
  );
}
