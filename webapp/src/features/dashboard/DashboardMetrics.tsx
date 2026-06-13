"use client";

import { useEffect, useState } from "react";
import { Briefcase, Layers, Send, Clock } from "lucide-react";
import { dashboardApi } from "@/shared/api/gateway";
import { Card, CardContent } from "@/shared/components/Card";
import { Skeleton } from "@/shared/components/Skeleton";
import type { DashboardMetrics } from "@/shared/api/types";

interface MetricCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
}

function MetricCard({ label, value, icon }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="pt-4 flex items-center gap-4">
        <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center text-accent-foreground shrink-0">
          {icon}
        </div>
        <div>
          <p className="text-2xl font-bold text-foreground">{value}</p>
          <p className="text-xs text-muted-foreground">{label}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function DashboardMetricsGrid() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    dashboardApi
      .metrics()
      .then(setMetrics)
      .catch(() => {})
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-24" />)}
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        label="Active Jobs"
        value={Object.values(metrics.jobs_by_source).reduce((a, b) => a + b, 0)}
        icon={<Briefcase className="h-5 w-5" />}
      />
      <MetricCard
        label="Pending Variants"
        value={metrics.variants_pending}
        icon={<Layers className="h-5 w-5" />}
      />
      <MetricCard
        label="Applications Today"
        value={metrics.applications_today}
        icon={<Send className="h-5 w-5" />}
      />
      <MetricCard
        label="Total Sent"
        value={metrics.applications_total}
        icon={<Clock className="h-5 w-5" />}
      />
    </div>
  );
}
