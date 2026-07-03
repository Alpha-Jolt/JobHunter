"use client";

import { useEffect, useState, useCallback } from "react";
import { companyDiscoveryApi, careerJobsApi } from "@/lib/api";
import {
  Building2,
  Play,
  RefreshCw,
  Activity,
  Mail,
  Cpu,
  Search,
  Database,
  AlertCircle,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

// ── Types ────────────────────────────────────────────────────────────────────

interface DiscoveryRunResponse {
  run_id: string;
  status: string;
  started_at: string;
}

interface RunStatus {
  run_id: string;
  source: string;
  started_at: string | null;
  completed_at: string | null;
  status: string;
  companies_found: number;
  errors: number;
  error_detail: string | null;
}

interface CompanyStats {
  total_companies: number;
  by_crawl_status: Record<string, number>;
  by_ats_platform: Record<string, number>;
  with_career_page_url: number;
  with_career_email: number;
  low_trust_email_count: number;
}

interface CareerJobCounts {
  total_jobs: number;
  by_status: Record<string, number>;
  by_extraction_method: Record<string, number>;
  active_companies_count: number;
  jobs_with_apply_contact: number;
}

// ── Status badge helper ───────────────────────────────────────────────────────

const STATUS_COLORS: Record<string, string> = {
  queued: "bg-yellow-100 text-yellow-800",
  running: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

function StatusBadge({ status }: { status: string }) {
  const cls = STATUS_COLORS[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase ${cls}`}>
      {status}
    </span>
  );
}

// ── Stat card ─────────────────────────────────────────────────────────────────

function StatCard({
  label,
  value,
  sub,
}: {
  label: string;
  value: string | number;
  sub?: string;
}) {
  return (
    <div className="bg-white rounded-xl shadow p-5">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

// ── ATS bar colours ───────────────────────────────────────────────────────────

const ATS_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#8b5cf6",
  "#ef4444", "#06b6d4", "#84cc16", "#f97316",
  "#ec4899", "#6366f1", "#14b8a6",
];

// ── Main page ─────────────────────────────────────────────────────────────────

export default function CompanyDiscoveryPage() {
  // --- Discovery form state
  const [role, setRole] = useState("software engineer");
  const [location, setLocation] = useState("Bangalore");
  const [experience, setExperience] = useState("fresher");
  const [salary, setSalary] = useState("");
  const [discoveryRunId, setDiscoveryRunId] = useState<string | null>(null);
  const [discoveryStatus, setDiscoveryStatus] = useState<RunStatus | null>(null);
  const [discoverySubmitting, setDiscoverySubmitting] = useState(false);
  const [discoveryError, setDiscoveryError] = useState("");

  // --- Bootstrap state
  const [selectedSources, setSelectedSources] = useState<string[]>(["all"]);
  const [bootstrapRunId, setBootstrapRunId] = useState<string | null>(null);
  const [bootstrapStatus, setBootstrapStatus] = useState<RunStatus | null>(null);
  const [bootstrapSubmitting, setBootstrapSubmitting] = useState(false);
  const [bootstrapError, setBootstrapError] = useState("");

  // --- Stats state
  const [companyStats, setCompanyStats] = useState<CompanyStats | null>(null);
  const [jobCounts, setJobCounts] = useState<CareerJobCounts | null>(null);
  const [statsError, setStatsError] = useState("");

  // ── Load stats ──────────────────────────────────────────────────────────────

  const loadStats = useCallback(async () => {
    try {
      const [statsRes, countsRes] = await Promise.all([
        companyDiscoveryApi.getStats(),
        careerJobsApi.getCounts(),
      ]);
      setCompanyStats(statsRes.data);
      setJobCounts(countsRes.data);
      setStatsError("");
    } catch {
      setStatsError("Failed to load statistics.");
    }
  }, []);

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 10_000);
    return () => clearInterval(interval);
  }, [loadStats]);

  // ── Poll discovery run ──────────────────────────────────────────────────────

  useEffect(() => {
    if (!discoveryRunId) return;
    const interval = setInterval(async () => {
      try {
        const res = await companyDiscoveryApi.getStatus(discoveryRunId);
        setDiscoveryStatus(res.data);
        if (res.data.status === "completed" || res.data.status === "failed") {
          clearInterval(interval);
          loadStats();
        }
      } catch {
        // keep polling
      }
    }, 5_000);
    return () => clearInterval(interval);
  }, [discoveryRunId, loadStats]);

  // ── Poll bootstrap run ──────────────────────────────────────────────────────

  useEffect(() => {
    if (!bootstrapRunId) return;
    const interval = setInterval(async () => {
      try {
        const res = await companyDiscoveryApi.getStatus(bootstrapRunId);
        setBootstrapStatus(res.data);
        if (res.data.status === "completed" || res.data.status === "failed") {
          clearInterval(interval);
          loadStats();
        }
      } catch {
        // keep polling
      }
    }, 5_000);
    return () => clearInterval(interval);
  }, [bootstrapRunId, loadStats]);

  // ── Handlers ────────────────────────────────────────────────────────────────

  const handleStartDiscovery = async (e: React.FormEvent) => {
    e.preventDefault();
    setDiscoveryError("");
    setDiscoverySubmitting(true);
    try {
      const res = await companyDiscoveryApi.startDiscovery({
        role,
        location,
        experience,
        salary: salary || undefined,
      });
      const data: DiscoveryRunResponse = res.data;
      setDiscoveryRunId(data.run_id);
      setDiscoveryStatus(null);
    } catch (err: any) {
      setDiscoveryError(err.response?.data?.detail ?? "Failed to start discovery.");
    } finally {
      setDiscoverySubmitting(false);
    }
  };

  const handleRunBootstrap = async () => {
    setBootstrapError("");
    setBootstrapSubmitting(true);
    try {
      const sources = selectedSources.includes("all") ? ["all"] : selectedSources;
      const res = await companyDiscoveryApi.runBootstrap({ sources });
      const data: DiscoveryRunResponse = res.data;
      setBootstrapRunId(data.run_id);
      setBootstrapStatus(null);
    } catch (err: any) {
      setBootstrapError(err.response?.data?.detail ?? "Failed to start bootstrap.");
    } finally {
      setBootstrapSubmitting(false);
    }
  };

  const toggleSource = (src: string) => {
    if (src === "all") {
      setSelectedSources(["all"]);
      return;
    }
    setSelectedSources((prev) => {
      const without = prev.filter((s) => s !== "all" && s !== src);
      if (prev.includes(src)) return without.length ? without : ["all"];
      return [...without, src];
    });
  };

  // ── Derived chart data ───────────────────────────────────────────────────────

  const atsChartData = companyStats
    ? Object.entries(companyStats.by_ats_platform)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => ({ name, value }))
        .sort((a, b) => b.value - a.value)
    : [];

  const crawlStatusData = companyStats
    ? Object.entries(companyStats.by_crawl_status)
        .filter(([, v]) => v > 0)
        .map(([name, value]) => ({ name, value }))
    : [];

  // ── Bootstrap source list ────────────────────────────────────────────────────

  const SOURCES = [
    { id: "datasets", label: "Open Datasets (GLEIF, Startup India, MCA21)" },
    { id: "vc_portfolio", label: "VC & Accelerator Portfolios" },
    { id: "github", label: "GitHub Organization Discovery" },
    { id: "directory", label: "Public Directories (Zauba, NASSCOM, CII)" },
  ];

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      {/* Page title */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <Building2 size={24} />
          Company Discovery
        </h1>
        <button
          onClick={loadStats}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800"
        >
          <RefreshCw size={16} />
          Refresh stats
        </button>
      </div>

      {statsError && (
        <div className="bg-red-50 text-red-600 p-3 rounded flex items-center gap-2 text-sm">
          <AlertCircle size={16} />
          {statsError}
        </div>
      )}

      {/* ── Section 1: Stats overview ── */}
      {companyStats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard label="Total Companies" value={companyStats.total_companies} />
          <StatCard
            label="With Career Page"
            value={companyStats.with_career_page_url}
            sub={
              companyStats.total_companies > 0
                ? `${Math.round((companyStats.with_career_page_url / companyStats.total_companies) * 100)}% of total`
                : undefined
            }
          />
          <StatCard
            label="Career Emails Found"
            value={companyStats.with_career_email}
            sub={
              companyStats.low_trust_email_count > 0
                ? `${companyStats.low_trust_email_count} low-trust`
                : undefined
            }
          />
          <StatCard
            label="Active Career Jobs"
            value={jobCounts?.by_status?.active ?? 0}
            sub={
              jobCounts
                ? `${jobCounts.active_companies_count} companies`
                : undefined
            }
          />
        </div>
      )}

      {/* ── Section 2: Controls ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Discovery Mode */}
        <div className="bg-white rounded-xl shadow p-6 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Search size={18} />
            Discovery Mode
          </h2>
          {discoveryError && (
            <div className="bg-red-50 text-red-500 p-3 rounded text-sm">{discoveryError}</div>
          )}
          <form onSubmit={handleStartDiscovery} className="space-y-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">Role keyword</label>
              <input
                className="w-full border p-2 rounded text-sm"
                value={role}
                onChange={(e) => setRole(e.target.value)}
                placeholder="e.g. full stack developer"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Location</label>
              <input
                className="w-full border p-2 rounded text-sm"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="e.g. Coimbatore"
                required
              />
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Experience level</label>
              <select
                className="w-full border p-2 rounded text-sm"
                value={experience}
                onChange={(e) => setExperience(e.target.value)}
              >
                <option value="fresher">Fresher</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-600 mb-1">Salary range (optional)</label>
              <input
                className="w-full border p-2 rounded text-sm"
                value={salary}
                onChange={(e) => setSalary(e.target.value)}
                placeholder="e.g. 5-10 LPA"
              />
            </div>
            <button
              type="submit"
              disabled={discoverySubmitting}
              className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <Play size={16} />
              {discoverySubmitting ? "Starting…" : "Start Discovery"}
            </button>
          </form>

          {/* Discovery run status */}
          {discoveryStatus && (
            <div className="border-t pt-4 space-y-1 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-500">Run status</span>
                <StatusBadge status={discoveryStatus.status} />
              </div>
              <p className="text-gray-600">
                Companies found: <strong>{discoveryStatus.companies_found}</strong>
              </p>
              {discoveryStatus.errors > 0 && (
                <p className="text-red-500">Errors: {discoveryStatus.errors}</p>
              )}
              {discoveryStatus.error_detail && (
                <p className="text-red-400 text-xs">{discoveryStatus.error_detail}</p>
              )}
            </div>
          )}
          {discoveryRunId && !discoveryStatus && (
            <p className="text-sm text-gray-400 animate-pulse flex items-center gap-1">
              <Activity size={14} /> Waiting for status…
            </p>
          )}
        </div>

        {/* Bootstrap Mode */}
        <div className="bg-white rounded-xl shadow p-6 space-y-4">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Database size={18} />
            Bootstrap Mode
          </h2>
          <p className="text-sm text-gray-500">
            Import company domains from public datasets and directories. No admin input required.
          </p>
          {bootstrapError && (
            <div className="bg-red-50 text-red-500 p-3 rounded text-sm">{bootstrapError}</div>
          )}

          <div className="space-y-2">
            <label className="block text-sm text-gray-600 mb-1">Sources to import</label>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="src-all"
                checked={selectedSources.includes("all")}
                onChange={() => toggleSource("all")}
                className="rounded"
              />
              <label htmlFor="src-all" className="text-sm cursor-pointer font-medium">
                All sources
              </label>
            </div>
            {SOURCES.map((src) => (
              <div key={src.id} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id={`src-${src.id}`}
                  checked={selectedSources.includes(src.id)}
                  onChange={() => toggleSource(src.id)}
                  disabled={selectedSources.includes("all")}
                  className="rounded"
                />
                <label
                  htmlFor={`src-${src.id}`}
                  className={`text-sm cursor-pointer ${
                    selectedSources.includes("all") ? "text-gray-400" : ""
                  }`}
                >
                  {src.label}
                </label>
              </div>
            ))}
          </div>

          <button
            onClick={handleRunBootstrap}
            disabled={bootstrapSubmitting}
            className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            <RefreshCw size={16} />
            {bootstrapSubmitting ? "Starting…" : "Run Bootstrap Import"}
          </button>

          {/* Bootstrap run status */}
          {bootstrapStatus && (
            <div className="border-t pt-4 space-y-1 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-gray-500">Run status</span>
                <StatusBadge status={bootstrapStatus.status} />
              </div>
              <p className="text-gray-600">
                Companies found: <strong>{bootstrapStatus.companies_found}</strong>
              </p>
              {bootstrapStatus.errors > 0 && (
                <p className="text-red-500">Errors: {bootstrapStatus.errors}</p>
              )}
              {bootstrapStatus.error_detail && (
                <p className="text-red-400 text-xs">{bootstrapStatus.error_detail}</p>
              )}
            </div>
          )}
          {bootstrapRunId && !bootstrapStatus && (
            <p className="text-sm text-gray-400 animate-pulse flex items-center gap-1">
              <Activity size={14} /> Waiting for status…
            </p>
          )}
        </div>
      </div>

      {/* ── Section 3: Charts ── */}
      {companyStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Crawl status breakdown */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
              <Activity size={18} />
              Crawl Status Breakdown
            </h2>
            {crawlStatusData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={crawlStatusData} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400">No data yet.</p>
            )}
          </div>

          {/* ATS platform breakdown */}
          <div className="bg-white rounded-xl shadow p-6">
            <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
              <Cpu size={18} />
              ATS Platform Breakdown
            </h2>
            {atsChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={atsChartData} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {atsChartData.map((_, index) => (
                      <Cell key={index} fill={ATS_COLORS[index % ATS_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm text-gray-400">No data yet.</p>
            )}
          </div>
        </div>
      )}

      {/* ── Section 4: Email stats row ── */}
      {companyStats && (
        <div className="bg-white rounded-xl shadow p-6">
          <h2 className="text-lg font-bold flex items-center gap-2 mb-4">
            <Mail size={18} />
            Email Stats
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-gray-500">Total companies</p>
              <p className="text-2xl font-bold">{companyStats.total_companies}</p>
            </div>
            <div>
              <p className="text-gray-500">Enriched (with career page)</p>
              <p className="text-2xl font-bold text-blue-600">{companyStats.with_career_page_url}</p>
            </div>
            <div>
              <p className="text-gray-500">With career email</p>
              <p className="text-2xl font-bold text-green-600">{companyStats.with_career_email}</p>
            </div>
            <div>
              <p className="text-gray-500">Low-trust emails</p>
              <p className="text-2xl font-bold text-yellow-600">{companyStats.low_trust_email_count}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
