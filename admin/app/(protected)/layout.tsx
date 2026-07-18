"use client";

import { useAuthStore } from "@/features/auth/authStore";
import { api } from "@/lib/api";
import { useRouter } from "next/navigation";
import { LogOut, LayoutDashboard, Building2, Briefcase } from "lucide-react";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const setAccessToken = useAuthStore((state) => state.setAccessToken);

  const handleLogout = async () => {
    try {
      await api.post("/auth/logout");
    } catch (e) {}
    setAccessToken(null);
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex bg-gray-100">
      <aside className="w-64 bg-gray-900 text-white flex flex-col">
        <div className="p-6 font-bold text-xl border-b border-gray-800">
          JobHunter Admin
        </div>
        <nav className="flex-1 p-4 space-y-2">
          <a href="/dashboard/scraper" className="flex items-center gap-3 p-3 rounded bg-gray-800 text-gray-200 hover:text-white">
            <LayoutDashboard size={20} />
            Scraper
          </a>
          <a href="/dashboard/company-discovery" className="flex items-center gap-3 p-3 rounded text-gray-400 hover:bg-gray-800 hover:text-white">
            <Building2 size={20} />
            Company Discovery
          </a>
          <a href="/dashboard/company-discovery/career-jobs" className="flex items-center gap-3 p-3 rounded text-gray-400 hover:bg-gray-800 hover:text-white">
            <Briefcase size={20} />
            Career Jobs
          </a>
          <a href="/dashboard/api-scraper" className="flex items-center gap-3 p-3 rounded text-gray-400 hover:bg-gray-800 hover:text-white">
            <LayoutDashboard size={20} />
            API Scrapers
          </a>
        </nav>
        <div className="p-4 border-t border-gray-800">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-3 p-3 w-full rounded text-red-400 hover:bg-gray-800 hover:text-red-300"
          >
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  );
}
