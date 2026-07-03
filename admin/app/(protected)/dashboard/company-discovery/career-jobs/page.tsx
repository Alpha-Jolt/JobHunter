"use client";

import { useEffect, useState, useCallback } from "react";
import { careerJobsApi } from "@/lib/api";
import {
  Briefcase,
  Play,
  RefreshCw,
  Activity,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  AlertCircle,
} from "lucide-react";

// ── Types ─────────────────────────────────────────────────────────────────────

interface CareerJobResponse {
  career_job_id: string;
  company_id: string;
  company_name: string | null;
  apex_domain: string | null;
  job_title: string;
  job_url: string;
  location: string | null;
  remote_type: string | null;
  job_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  experience_min: number | null;
  experience_max: number | null;
  skills_required: string[];
  apply_email: string | null;
  apply_url: string | null;
  ats_platform: string | null;
  extraction_method: string;
  posted_at: string | null;
  scraped_at: string | null;
  last_seen_at: string | null;
  status: string;
  source_channel: string;
}

interface CareerJobsListResponse {
  jobs: CareerJobResponse[];
  total: number;
  limit: number;
  offset: number;
}

interface CareerJobCounts {
  total_jobs: number;
  by_status: Record<string, number>;
  by_extraction_method: Record<string, number>;
  active_companies_count: number;
  jobs_with_apply_contact: number;
}

interface ScrapeRunResponse {
  run_id: string;
  status: string;
  started_at: string;
}

interface ScrapeStatus {
  run_id: string;
  source: string;
  started_at: string | null;
  completed_at: string | null;
  status: string;
  jobs_found: number;
  errors: number;
  error_detail: string | null;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  closed: "bg-gray-100 text-gray-600",
  raw: "bg-yellow-100 text-yellow-800",
  queued: "bg-yellow-100 text-yellow-800",
  running: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

function Badge({ label }: { label: string }) {
  const cls = STATUS_COLORS[label] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${cls}`}>
      {label}
    </span>
  );
}

function fmtDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function salaryLabel(min: number | null, max: number | null): string {
  if (!min && !max) return "—";
  if (min && max) return `₹${(min / 100000).toFixed(1)}L – ₹${(max / 100000).toFixed(1)}L`;
  if (min) return `₹${(min / 100000).toFixed(1)}L+`;
  return `up to ₹${(max! / 100000).toFixed(1)}L`;
}

const PAGE_SIZE = 50;

// ── Main page ─────────────────────────────────────────────────────────────────

export default function CareerJobsPage() {
  const [jobs, setJobs] = useState<CareerJobResponse[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [counts, setCounts] = useState<CareerJobCounts | null>(null);

  const [companyFilter, setCompanyFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("active");

  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<ScrapeStatus | null>(null);
  const [scrapeSubmitting, setScrapeSubmitting] = useState(false);
  const [scrapeError, setScrapeError] = useState("");

  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState("");

  // ── Fetch jobs ────────────────────────────────────────────────────────────

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setFetchError("");
    try {
      const res = await careerJobsApi.getLatest({
        status: statusFilter || undefined,
        limit: PAGE_SIZE,
        offset,
      });
      const data: CareerJobsListResponse = res.data;
      setJobs(data.jobs);
      setTotal(data.total);
    } catch {
      setFetchError("Failed to load jobs.");
    } finally {
      setLoading(false);
    }
  }, [statusFilter, offset]);

  const fetchCounts = useCallback(async () => {
    try {
      const res = await careerJobsApi.getCounts();
      setCounts(res.data);
    } catch {
      // silent
    }
  }, []);

  useEffect(() => {
    fetchJobs();
    fetchCounts();
  }, [fetchJobs, fetchCounts]);

  // ── Poll run status ───────────────────────────────────────────────────────

  useEffect(() => {
    if (!runId) return;
    const interval = setInterval(async () => {
      try {
        const res = await careerJobsApi.getStatus(runId);
        setRunStatus(res.data);
        if (res.data.status === "completed" || res.data.status === "failed") {
          clearInterval(interval);
          fetchJobs();
          fetchCounts();
        }
      } catch {
        // keep polling
      }
    }, 5_000);
    return () => clearInterval(interval);
  }, [runId, fetchJobs, fetchCounts]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const handleTriggerScrape = async () => {
    setScrapeError("");
    setScrapeSubmitting(true);
    try {
      const res = await careerJobsApi.startScrape();
      const data: ScrapeRunResponse = res.data;
      setRunId(data.run_id);
      setRunStatus(null);
    } catch (err: any) {
      setScrapeError(err.response?.data?.detail ?? "Failed to start scrape.");
    } finally {
      setScrapeSubmitting(false);
    }
  };

  // ── Filtered jobs (client-side company name filter) ───────────────────────

  const visibleJobs = companyFilter.trim()
    ? jobs.filter(
        (j) =>
          (j.company_name ?? "").toLowerCase().includes(companyFilter.toLowerCase()) ||
          (j.apex_domain ?? "").toLowerCase().includes(companyFilter.toLowerCase())
      )
    : jobs;

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Briefcase size={24} />
          Career Jobs
        </h1>
        <button
          onClick={() => { fetchJobs(); fetchCounts(); }}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800"
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Stats row */}
      {counts && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-xl shadow p-4">
            <p className="text-sm text-gray-500">Total Jobs</p>
            <p className="text-3xl font-bold mt-1">{counts.total_jobs}</p>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <p className="text-sm text-gray-500">Active</p>
            <p className="text-3xl font-bold mt-1 text-green-600">
              {counts.by_status.active ?? 0}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <p className="text-sm text-gray-500">Companies with Jobs</p>
            <p className="text-3xl font-bold mt-1 text-blue-600">
              {counts.active_companies_count}
            </p>
          </div>
          <div className="bg-white rounded-xl shadow p-4">
            <p className="text-sm text-gray-500">With Apply Contact</p>
            <p className="text-3xl font-bold mt-1 text-purple-600">
              {counts.jobs_with_apply_contact}
            </p>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="bg-white rounded-xl shadow p-5 flex flex-col md:flex-row gap-4 items-start md:items-end">
        <div className="flex-1">
          <label className="block text-sm text-gray-600 mb-1">Filter by company / domain</label>
          <input
            className="w-full border p-2 rounded text-sm"
            value={companyFilter}
            onChange={(e) => setCompanyFilter(e.target.value)}
            placeholder="e.g. acme or acme.com"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Status</label>
          <select
            className="border p-2 rounded text-sm"
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setOffset(0); }}
          >
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
            <option value="raw">Raw</option>
          </select>
        </div>
        <div className="flex flex-col gap-1 min-w-[200px]">
          {scrapeError && (
            <p className="text-red-500 text-xs flex items-center gap-1">
              <AlertCircle size={12} />
              {scrapeError}
            </p>
          )}
          <button
            onClick={handleTriggerScrape}
            disabled={scrapeSubmitting}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2 text-sm"
          >
            <Play size={14} />
            {scrapeSubmitting ? "Starting…" : "Trigger Career Scan (All)"}
          </button>
        </div>
      </div>

      {/* Run status */}
      {runStatus && (
        <div className="bg-white rounded-xl shadow p-4 flex items-center gap-4 text-sm">
          <span className="text-gray-500">Scan run:</span>
          <Badge label={runStatus.status} />
          <span className="text-gray-600">
            Jobs found: <strong>{runStatus.jobs_found}</strong>
          </span>
          {runStatus.errors > 0 && (
            <span className="text-red-500">Errors: {runStatus.errors}</span>
          )}
        </div>
      )}
      {runId && !runStatus && (
        <p className="text-sm text-gray-400 animate-pulse flex items-center gap-1">
          <Activity size={14} /> Waiting for scan status…
        </p>
      )}

      {/* Table */}
      {fetchError && (
        <div className="bg-red-50 text-red-600 p-3 rounded flex items-center gap-2 text-sm">
          <AlertCircle size={16} />
          {fetchError}
        </div>
      )}

      <div className="bg-white rounded-xl shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-3 font-medium text-gray-600">Company</th>
                <th className="text-left p-3 font-medium text-gray-600">Job Title</th>
                <th className="text-left p-3 font-medium text-gray-600">Location</th>
                <th className="text-left p-3 font-medium text-gray-600">Type</th>
                <th className="text-left p-3 font-medium text-gray-600">Salary</th>
                <th className="text-left p-3 font-medium text-gray-600">Method</th>
                <th className="text-left p-3 font-medium text-gray-600">Posted</th>
                <th className="text-left p-3 font-medium text-gray-600">Status</th>
                <th className="text-left p-3 font-medium text-gray-600">Apply</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-gray-400">
                    Loading…
                  </td>
                </tr>
              ) : visibleJobs.length === 0 ? (
                <tr>
                  <td colSpan={9} className="p-6 text-center text-gray-400">
                    No jobs found.
                  </td>
                </tr>
              ) : (
                visibleJobs.map((job) => (
                  <tr key={job.career_job_id} className="hover:bg-gray-50">
                    <td className="p-3">
                      <p className="font-medium">{job.company_name ?? "—"}</p>
                      {job.apex_domain && (
                        <p className="text-xs text-gray-400">{job.apex_domain}</p>
                      )}
                    </td>
                    <td className="p-3 max-w-[200px]">
                      <p className="truncate font-medium">{job.job_title}</p>
                      {job.remote_type && (
                        <p className="text-xs text-gray-400 capitalize">{job.remote_type}</p>
                      )}
                    </td>
                    <td className="p-3 text-gray-600">{job.location ?? "—"}</td>
                    <td className="p-3">
                      {job.job_type ? (
                        <Badge label={job.job_type} />
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                    <td className="p-3 text-gray-600 whitespace-nowrap">
                      {salaryLabel(job.salary_min, job.salary_max)}
                    </td>
                    <td className="p-3">
                      <span className="text-xs text-gray-500 font-mono bg-gray-100 px-1.5 py-0.5 rounded">
                        {job.extraction_method.replace("_", " ")}
                      </span>
                    </td>
                    <td className="p-3 text-gray-500 whitespace-nowrap">
                      {fmtDate(job.posted_at ?? job.scraped_at)}
                    </td>
                    <td className="p-3">
                      <Badge label={job.status} />
                    </td>
                    <td className="p-3">
                      {job.apply_url ? (
                        <a
                          href={job.apply_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800"
                          title={job.apply_url}
                        >
                          <ExternalLink size={14} />
                        </a>
                      ) : job.apply_email ? (
                        <a
                          href={`mailto:${job.apply_email}`}
                          className="text-blue-600 hover:text-blue-800 text-xs"
                        >
                          {job.apply_email}
                        </a>
                      ) : (
                        <span className="text-gray-400">—</span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t text-sm text-gray-600">
            <span>
              Page {currentPage} of {totalPages} — {total} total
            </span>
            <div className="flex gap-2">
              <button
                onClick={() => setOffset(Math.max(0, offset - PAGE_SIZE))}
                disabled={offset === 0}
                className="flex items-center gap-1 px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
              >
                <ChevronLeft size={14} />
                Prev
              </button>
              <button
                onClick={() => setOffset(offset + PAGE_SIZE)}
                disabled={offset + PAGE_SIZE >= total}
                className="flex items-center gap-1 px-3 py-1 border rounded hover:bg-gray-50 disabled:opacity-40"
              >
                Next
                <ChevronRight size={14} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
