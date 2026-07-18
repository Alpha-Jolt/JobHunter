"use client";

import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Button } from "@/shared/components/Button";
import { useJobStore } from "@/shared/state/jobStore";
import { cn } from "@/shared/utils/cn";

const SOURCES = ["", "naukri", "indeed", "linkedin", "apify", "hunter"];

export function JobFilters() {
  const { filters, setFilters } = useJobStore();
  const [localSearch, setLocalSearch] = useState(filters.search);

  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearch !== filters.search) {
        setFilters({ search: localSearch });
      }
    }, 500);
    return () => clearTimeout(timer);
  }, [localSearch, filters.search, setFilters]);

  return (
    <div className="flex flex-col gap-3 mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search title, company, or keywords…"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className={cn(
            "h-11 w-full rounded-[var(--radius-sm)] border border-input-border bg-input pl-10 pr-3 text-[15px]",
            "transition-[border-color,box-shadow] duration-200",
            "focus:outline-none focus:border-primary focus:shadow-[0_0_0_3px_var(--ember-glow)]"
          )}
        />
      </div>
      <div className="flex flex-wrap gap-2">
        {SOURCES.map((s) => {
          const active = filters.source === s || (!s && !filters.source);
          return (
            <Button
              key={s || "all"}
              size="sm"
              variant={active ? "default" : "outline"}
              onClick={() => setFilters({ source: s || undefined })}
              className={cn(!active && "bg-card")}
            >
              {s || "All"}
            </Button>
          );
        })}
      </div>
    </div>
  );
}
