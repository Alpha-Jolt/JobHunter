"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Fredoka } from "next/font/google";
import { LayoutDashboard, Briefcase, FileText, Layers, Send, Menu, X, Bell } from "lucide-react";
import { cn } from "@/shared/utils/cn";
import { useUiStore } from "@/shared/state/uiStore";
import { ThemeToggle } from "./ThemeToggle";
import { UserMenu } from "./UserMenu";

const fredoka = Fredoka({ subsets: ["latin"], weight: ["600"] });

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
      {/* Top Header */}
      <header className="fixed top-0 inset-x-0 lg:left-64 z-40 h-14 border-b border-border bg-card flex items-center px-4 gap-3 transition-all">
        <button
          className="lg:hidden p-2 rounded-md hover:bg-secondary"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>

        {/* Global Search */}
        {/* <div className="flex-1 max-w-md hidden sm:flex items-center gap-2 px-3 py-1.5 bg-secondary rounded-full border border-transparent focus-within:border-border">
          <Search className="h-4 w-4 text-foreground-muted" />
          <input 
            type="text" 
            placeholder="Search..." 
            className="bg-transparent border-none outline-none text-sm w-full"
          />
        </div> */}

        <div className="ml-auto flex items-center gap-2">
          <button className="p-2 text-foreground-muted hover:text-foreground rounded-full hover:bg-secondary">
            <Bell className="h-5 w-5" />
          </button>
          <ThemeToggle />
          <UserMenu />
        </div>
      </header>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar (Desktop + Mobile) */}
      <aside
        className={cn(
          "fixed top-0 left-0 bottom-0 z-50 w-64 bg-card border-r border-border transition-transform lg:translate-x-0 flex flex-col",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        <div className="h-14 flex items-center px-4 border-b border-border justify-between lg:justify-center">
          <Link href="/dashboard" className={cn("text-2xl font-bold tracking-wide", fredoka.className)}>
            <span className="text-brand-charcoal dark:text-foreground">Job</span>
            <span className="text-brand-orange">Hunter</span>
          </Link>
          <button
            className="lg:hidden p-2 rounded-md hover:bg-secondary"
            onClick={() => setSidebarOpen(false)}
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex flex-col gap-1 p-3 flex-1 overflow-y-auto">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              onClick={() => setSidebarOpen(false)}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors",
                pathname.startsWith(href)
                  ? "bg-accent text-accent-foreground"
                  : "text-foreground-muted hover:bg-secondary hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          ))}
        </nav>
      </aside>
    </>
  );
}
