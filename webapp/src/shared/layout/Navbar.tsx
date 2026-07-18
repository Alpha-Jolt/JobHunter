"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { LayoutDashboard, Briefcase, FileText, Layers, Send, Menu, X, Bell } from "lucide-react";
import { cn } from "@/shared/utils/cn";
import { useUiStore } from "@/shared/state/uiStore";
import { ThemeToggle } from "./ThemeToggle";
import { UserMenu } from "./UserMenu";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/resume", label: "Resume", icon: FileText },
  { href: "/variants", label: "Variants", icon: Layers },
  { href: "/applications", label: "Applications", icon: Send },
];

export function Navbar() {
  const pathname = usePathname();
  const { sidebarOpen, setSidebarOpen } = useUiStore();

  return (
    <>
      <header className="fixed top-0 inset-x-0 lg:left-64 z-40 h-14 border-b border-border bg-card/80 backdrop-blur-xl flex items-center px-4 gap-3">
        <button
          className="lg:hidden p-2 rounded-[var(--radius-sm)] hover:bg-secondary transition-colors"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>

        <div className="ml-auto flex items-center gap-1.5">
          <button
            className="p-2 text-foreground-muted hover:text-foreground rounded-full hover:bg-secondary transition-colors"
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
          </button>
          <ThemeToggle />
          <UserMenu />
        </div>
      </header>

      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            className="fixed inset-0 z-30 bg-ink/40 backdrop-blur-[2px] lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      <aside
        className={cn(
          "fixed top-0 left-0 bottom-0 z-50 w-64 bg-card border-r border-border transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] lg:translate-x-0 flex flex-col",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-14 flex items-center px-5 border-b border-border justify-between lg:justify-start">
          <Link href="/dashboard" className="font-brand text-[1.55rem] font-semibold tracking-wide leading-none">
            <span className="text-brand-charcoal">Job</span>
            <span className="text-ember">Hunter</span>
          </Link>
          <button
            className="lg:hidden p-2 rounded-[var(--radius-sm)] hover:bg-secondary"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex flex-col gap-0.5 p-3 flex-1 overflow-y-auto">
          <p className="font-mono-label text-muted-foreground px-3 py-2 mb-1">Workspace</p>
          {navItems.map(({ href, label, icon: Icon }) => {
            const active = pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setSidebarOpen(false)}
                className={cn(
                  "group relative flex items-center gap-3 px-3 py-2.5 rounded-[var(--radius-sm)] text-sm font-medium transition-colors duration-200",
                  active
                    ? "nav-item-active"
                    : "text-foreground-muted hover:bg-secondary hover:text-foreground"
                )}
              >
                <Icon className={cn("h-4 w-4 transition-colors", active ? "text-ember" : "opacity-80")} />
                {label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-border">
          <p className="font-mono-label text-muted-foreground mb-1">Apply smart</p>
          <p className="text-xs text-foreground-muted leading-relaxed">
            Tailor. Approve. Send — one queue at a time.
          </p>
        </div>
      </aside>
    </>
  );
}
