"use client";

import { useEffect, useCallback } from "react";
import { jobsApi } from "@/shared/api/gateway";
import { useJobStore } from "@/shared/state/jobStore";
import { useUiStore } from "@/shared/state/uiStore";

export function useJobs() {
  const { jobs, total, filters, isLoading, error, setJobs, setLoading, setError } = useJobStore();
  const { addToast } = useUiStore();

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await jobsApi.list({
        source: filters.source,
        limit: filters.limit,
        offset: filters.offset,
      });
      setJobs(data.jobs, data.total ?? data.jobs.length);
    } catch {
      const msg = "Failed to load jobs.";
      setError(msg);
      addToast("error", msg);
    } finally {
      setLoading(false);
    }
  }, [filters, setJobs, setLoading, setError, addToast]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return { jobs, total, filters, isLoading, error, refetch: fetchJobs };
}
