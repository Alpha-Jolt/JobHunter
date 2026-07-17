"use client";

import { useState, useEffect } from "react";
import { Search } from "lucide-react";
import { Button } from "@/shared/components/Button";
import { useJobStore } from "@/shared/state/jobStore";

const SOURCES = ["", "naukri", "indeed"];

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
    <div className="flex flex-col sm:flex-row gap-3 mb-6">
      <div className="relative flex-1">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="Search jobs…"
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="h-11 w-full rounded-md border border-input-border bg-input pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>
      <div className="flex gap-2">
        {SOURCES.map((s) => (
          <Button
            key={s || "all"}
            size="sm"
            variant={filters.source === s || (!s && !filters.source) ? "default" : "outline"}
            onClick={() => setFilters({ source: s || undefined })}
          >
            {s || "All"}
          </Button>
        ))}
      </div>
    </div>
  );
}
