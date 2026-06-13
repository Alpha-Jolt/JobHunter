"use client";

import { useJobStore } from "@/shared/state/jobStore";
import { useVariants } from "@/features/variants/useVariants";
import { useUserProfileStore } from "@/shared/state/userProfileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { useJobs } from "@/features/jobs/useJobs";
import { JobCard } from "@/features/jobs/JobCard";
import { JobFilters } from "@/features/jobs/JobFilters";
import { Skeleton } from "@/shared/components/Skeleton";
import type { JobRecord } from "@/shared/api/types";

export default function JobsPage() {
  const { jobs, isLoading } = useJobs();
  const { filters, setSelectedJob } = useJobStore();
  const { resumeKey } = useUserProfileStore();
  const { generate } = useVariants();
  const { addToast } = useUiStore();

  const filteredJobs = filters.search
    ? jobs.filter(
        (j) =>
          j.title.toLowerCase().includes(filters.search.toLowerCase()) ||
          j.company_name.toLowerCase().includes(filters.search.toLowerCase())
      )
    : jobs;

  const handleSelect = async (job: JobRecord) => {
    if (!resumeKey) {
      addToast("warning", "Upload your resume first before generating a variant.");
      return;
    }
    setSelectedJob(job);
    await generate(job.job_id, resumeKey);
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
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredJobs.map((job) => (
            <JobCard key={job.job_id} job={job} onSelect={handleSelect} />
          ))}
        </div>
      )}
    </div>
  );
}
