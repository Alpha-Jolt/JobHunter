"use client";

import { useState, useEffect } from "react";
import { useJobStore } from "@/shared/state/jobStore";
import { useVariants } from "@/features/variants/useVariants";
import { useUserProfileStore } from "@/shared/state/userProfileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { useJobs } from "@/features/jobs/useJobs";
import { JobCard } from "@/features/jobs/JobCard";
import { JobFilters } from "@/features/jobs/JobFilters";
import { Skeleton } from "@/shared/components/Skeleton";
import { Button } from "@/shared/components/Button";
import type { JobRecord } from "@/shared/api/types";

export default function JobsPage() {
  const { jobs, total, isLoading } = useJobs();
  const { filters, setFilters, setSelectedJob } = useJobStore();
  const { resumeKey } = useUserProfileStore();
  const { generate } = useVariants();
  const { addToast } = useUiStore();

  const [pageInput, setPageInput] = useState("");
  const [generatingJobId, setGeneratingJobId] = useState<string | null>(null);

  const limit = filters.limit || 20;
  const currentPage = Math.floor((filters.offset || 0) / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  useEffect(() => {
    setPageInput(currentPage.toString());
  }, [currentPage]);

  // Filtering is now handled by the backend
  const filteredJobs = jobs;

  const handleSelect = async (job: JobRecord) => {
    if (!resumeKey) {
      addToast("warning", "Upload your resume first before generating a variant.");
      return;
    }
    setGeneratingJobId(job.job_id);
    setSelectedJob(job);
    await generate(job.job_id, resumeKey);
    setGeneratingJobId(null);
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
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Jobs</h1>
        <p className="text-sm text-muted-foreground mt-1">Discover and apply to matching roles.</p>
      </div>

      <JobFilters />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => <Skeleton key={i} className="h-52" />)}
        </div>
      ) : filteredJobs.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground text-sm">
          No jobs found. Try adjusting your filters.
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredJobs.map((job) => (
              <JobCard
                key={job.job_id}
                job={job}
                onSelect={handleSelect}
                isGenerating={generatingJobId === job.job_id}
              />
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6 p-4 border-t border-border">
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
                  className="h-8 w-16 rounded-md border border-input-border bg-input px-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-ring"
                />
                <span className="text-sm text-muted-foreground">of {totalPages}</span>
                <button type="submit" className="hidden">Go</button>
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
