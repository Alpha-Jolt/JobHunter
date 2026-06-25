"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { Play, Activity, List } from "lucide-react";

interface ScraperStatus {
  state: string;
  raw: number;
  final: number;
  error: string | null;
}

export default function ScraperPage() {
  const [source, setSource] = useState("naukri");
  const [keywords, setKeywords] = useState("Python");
  const [locations, setLocations] = useState("Bangalore");
  const [experience, setExperience] = useState("0-2");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<ScraperStatus | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const triggerScrape = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitError("");
    setIsSubmitting(true);
    try {
      const res = await api.post("/scraper/trigger", {
        source,
        keywords: keywords.split(",").map((k) => k.trim()),
        locations: locations.split(",").map((l) => l.trim()),
        experience,
      });
      setTaskId(res.data.task_id);
    } catch (err: any) {
      setSubmitError(err.response?.data?.detail || "Failed to start scraper.");
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/scraper/status/${taskId}`);
        setStatus(res.data);
        if (res.data.state === "completed" || res.data.state === "failed") {
          clearInterval(interval);
        }
      } catch (err) {
        console.error(err);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [taskId]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get("/scraper/logs?limit=50");
        setLogs(res.data.logs ?? []);
      } catch (err) {
        console.error(err);
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8">
      {/* Trigger Form */}
      <div className="bg-white p-6 rounded-xl shadow">
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
          <Play size={20} /> Trigger Scraper &amp; Preferences
        </h2>
        {submitError && (
          <div className="bg-red-50 text-red-500 p-3 rounded mb-4 text-sm">{submitError}</div>
        )}
        <form onSubmit={triggerScrape} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Source</label>
            <select
              className="w-full border p-2 rounded"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            >
              <option value="naukri">Naukri</option>
              <option value="indeed">Indeed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm mb-1">Keywords (comma-separated)</label>
            <input
              className="w-full border p-2 rounded"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Locations (comma-separated)</label>
            <input
              className="w-full border p-2 rounded"
              value={locations}
              onChange={(e) => setLocations(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm mb-1">Experience</label>
            <input
              className="w-full border p-2 rounded"
              value={experience}
              onChange={(e) => setExperience(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isSubmitting ? "Starting..." : "Save Preferences & Start Scraper"}
          </button>
        </form>
      </div>

      {/* Status & Logs */}
      <div className="space-y-8">
        <div className="bg-white p-6 rounded-xl shadow">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-4">
            <Activity size={20} /> Current Task Status
          </h2>
          {status ? (
            <div className="space-y-2">
              <p>
                <strong>State:</strong>{" "}
                <span
                  className={`uppercase font-semibold ${
                    status.state === "completed"
                      ? "text-green-600"
                      : status.state === "failed"
                      ? "text-red-600"
                      : "text-blue-600"
                  }`}
                >
                  {status.state}
                </span>
              </p>
              <p><strong>Raw Jobs:</strong> {status.raw}</p>
              <p><strong>Final Jobs:</strong> {status.final}</p>
              {status.error && (
                <p className="text-red-500">
                  <strong>Error:</strong> {status.error}
                </p>
              )}
            </div>
          ) : (
            <p className="text-gray-500">No active task.</p>
          )}
        </div>

        <div
          id="log-viewer"
          className="bg-gray-900 p-6 rounded-xl shadow text-green-400 font-mono text-sm h-64 overflow-y-auto"
        >
          <h2 className="text-white font-bold flex items-center gap-2 mb-4 font-sans text-base">
            <List size={20} /> Live Logs
          </h2>
          {logs.length === 0 ? (
            <p className="text-gray-500">No logs yet.</p>
          ) : (
            logs.map((log, i) => <div key={i}>{log}</div>)
          )}
        </div>
      </div>
    </div>
  );
}
