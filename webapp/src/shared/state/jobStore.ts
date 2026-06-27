import { create } from "zustand";
import type { JobRecord } from "@/shared/api/types";

interface JobFilters {
  source?: string;
  search: string;
  limit: number;
  offset: number;
}

interface JobState {
  jobs: JobRecord[];
  total: number;
  filters: JobFilters;
  selectedJob: JobRecord | null;
  isLoading: boolean;
  error: string | null;
}

interface JobActions {
  setJobs: (jobs: JobRecord[], total: number) => void;
  setFilters: (f: Partial<JobFilters>) => void;
  setSelectedJob: (job: JobRecord | null) => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
  reset: () => void;
}

const defaultFilters: JobFilters = { search: "", limit: 20, offset: 0 };

export const useJobStore = create<JobState & JobActions>((set) => ({
  jobs: [],
  total: 0,
  filters: defaultFilters,
  selectedJob: null,
  isLoading: false,
  error: null,

  setJobs: (jobs, total) => set({ jobs, total }),
  setFilters: (f) => set((s) => ({ filters: { ...s.filters, ...f, offset: f.offset !== undefined ? f.offset : 0 } })),
  setSelectedJob: (job) => set({ selectedJob: job }),
  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
  reset: () => set({ jobs: [], total: 0, filters: defaultFilters }),
}));
