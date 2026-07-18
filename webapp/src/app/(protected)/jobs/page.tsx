"use client";

import { useState, useEffect } from "react";
import { useAuthStore } from "@/shared/state/authStore";
import { useJobStore } from "@/shared/state/jobStore";
import { useUserProfileStore } from "@/shared/state/userProfileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { useJobs } from "@/features/jobs/useJobs";
import { JobCard } from "@/features/jobs/JobCard";
import { JobFilters } from "@/features/jobs/JobFilters";
import { Skeleton } from "@/shared/components/Skeleton";
import { Button } from "@/shared/components/Button";
import { PageHeader } from "@/shared/components/Motion";
import { config } from "@/lib/config";
import { getAccessToken } from "@/shared/api/client";
import type { JobRecord } from "@/shared/api/types";

export default function JobsPage() {
  const { jobs, total, isLoading } = useJobs();
  const { filters, setFilters } = useJobStore();
  const { resumeKey } = useUserProfileStore();
  const { user } = useAuthStore();
  const { addToast } = useUiStore();

  const [pageInput, setPageInput] = useState("");
  const [selectedJobIds, setSelectedJobIds] = useState<Set<string>>(new Set());
  const [isBulkGenerating, setIsBulkGenerating] = useState(false);
  const [bulkProgress, setBulkProgress] = useState("");

  const limit = filters.limit || 20;
  const currentPage = Math.floor((filters.offset || 0) / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  useEffect(() => {
    setPageInput(currentPage.toString());
  }, [currentPage]);

  // Filtering is now handled by the backend
  const filteredJobs = jobs;

  const handleSelect = (job: JobRecord) => {
    const next = new Set(selectedJobIds);
    if (next.has(job.job_id)) next.delete(job.job_id);
    else if (next.size < 100) next.add(job.job_id);
    else addToast("warning", "You can only select up to 100 jobs at a time.");
    setSelectedJobIds(next);
  };

  const handleBulkGenerate = async () => {
    if (!resumeKey) {
      addToast("warning", "Upload your resume first before generating variants.");
      return;
    }
    
    setIsBulkGenerating(true);
    setBulkProgress("Starting...");
    
    try {
      const token = getAccessToken();
      const response = await fetch(`${config.apiBaseUrl}/api/ai/bulk-generate`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ 
          user_id: user?.user_id || "",
          job_ids: Array.from(selectedJobIds),
          resume_file_path: resumeKey
        })
      });

      if (!response.ok) {
        throw new Error("Failed to start bulk generation");
      }

      if (!response.body) {
        throw new Error("No response body");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      let isDone = false;
      while (!isDone) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split("\n");
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.status === "Error" || data.message.startsWith("Warning:")) {
                addToast("error", data.message);
              } else if (data.status === "Success") {
                setBulkProgress("Success");
                addToast("success", "Bulk variant generation completed.");
                setSelectedJobIds(new Set());
                isDone = true;
              } else {
                setBulkProgress(data.message);
              }
            } catch {
              // ignore parse errors for partial chunks
            }
          }
        }
      }
    } catch (err: unknown) {
      addToast("error", err instanceof Error ? err.message : "Failed to bulk generate variants.");
    } finally {
      setIsBulkGenerating(false);
      setTimeout(() => setBulkProgress(""), 2000);
    }
  };

  const handlePageSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    let targetPage = parseInt(pageInput, 10);
    if (isNaN(targetPage) || targetPage < 1) targetPage = 1;
    // We allow jumping to any page, even beyond totalPages, as requested by user.
    // "where if user start in page 1 and directly moved to page 30 or randomly to page 6, it should not produce any problems"
    setFilters({ offset: (targetPage - 1) * limit });
  };

  return (
    <div className="flex flex-col gap-2">
      <PageHeader
        label="Queue"
        title="Open roles"
        description="Discover matching jobs, select a batch, and generate tailored variants."
        actions={
          selectedJobIds.size > 0 ? (
            <div className="flex items-center gap-3 bg-card px-4 py-2.5 rounded-[var(--radius-sm)] border border-border-strong shadow-[0_12px_32px_-18px_rgba(16,16,18,0.35)]">
              <span className="font-mono-label text-foreground">{selectedJobIds.size} selected</span>
              <Button size="sm" onClick={handleBulkGenerate} disabled={isBulkGenerating}>
                {isBulkGenerating ? (
                  <span className="flex items-center gap-2">
                    <span className="h-3.5 w-3.5 rounded-full border-2 border-primary-foreground border-r-transparent animate-spin" />
                    {bulkProgress}
                  </span>
                ) : (
                  "Generate Variants"
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setSelectedJobIds(new Set())}
                disabled={isBulkGenerating}
              >
                Clear
              </Button>
            </div>
          ) : undefined
        }
      />

      <JobFilters />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Skeleton key={i} className="h-52 rounded-[var(--radius)]" />
          ))}
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="text-center py-20 border border-dashed border-border-strong rounded-[var(--radius)]">
          <p className="font-display text-lg text-foreground">No roles in view</p>
          <p className="text-sm text-muted-foreground mt-2">Try adjusting your filters or search.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.job_id}
                job={job}
                onSelect={handleSelect}
                isSelected={selectedJobIds.has(job.job_id)}
              />
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-8 pt-5 border-t border-border">
            <div className="text-sm text-muted-foreground">
              Showing {jobs.length > 0 ? (currentPage - 1) * limit + 1 : 0} to{" "}
              {Math.min(currentPage * limit, total)} of {total} jobs
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setFilters({ offset: Math.max(0, (currentPage - 2) * limit) })}
                disabled={currentPage <= 1 || isLoading}
              >
                Previous
              </Button>

              <form onSubmit={handlePageSubmit} className="flex items-center gap-2 mx-2">
                <span className="text-sm text-muted-foreground">Page</span>
                <input
                  type="number"
                  min="1"
                  value={pageInput}
                  onChange={(e) => setPageInput(e.target.value)}
                  className="h-8 w-16 rounded-[var(--radius-sm)] border border-input-border bg-input px-2 text-sm text-center focus:outline-none focus:border-primary focus:shadow-[0_0_0_3px_var(--ember-glow)]"
                />
                <span className="text-sm text-muted-foreground">of {totalPages}</span>
                <button type="submit" className="hidden">
                  Go
                </button>
              </form>

              <Button
                variant="outline"
                size="sm"
                onClick={() => setFilters({ offset: currentPage * limit })}
                disabled={currentPage >= totalPages || isLoading}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
