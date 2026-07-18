"use client";

import { useEffect, useState } from "react";
import { Briefcase, Layers, Send, Clock } from "lucide-react";
import { motion } from "framer-motion";
import { dashboardApi } from "@/shared/api/gateway";
import { Card, CardContent } from "@/shared/components/Card";
import { Skeleton } from "@/shared/components/Skeleton";
import type { DashboardMetrics } from "@/shared/api/types";

interface MetricCardProps {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  index: number;
}

function MetricCard({ label, value, icon, index }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.06, ease: [0.16, 1, 0.3, 1] }}
    >
      <Card className="h-full">
        <CardContent className="pt-5 flex items-center gap-4">
          <div className="h-11 w-11 rounded-[var(--radius-sm)] bg-accent flex items-center justify-center text-accent-foreground shrink-0">
            {icon}
          </div>
          <div>
            <p className="font-display text-2xl font-medium text-foreground tabular-nums leading-none">
              {value}
            </p>
            <p className="font-mono-label text-muted-foreground mt-2">{label}</p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
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
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24 rounded-[var(--radius)]" />
        ))}
      </div>
    );
  }

  if (!metrics) return null;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        index={0}
        label="Active Jobs"
        value={Object.values(metrics.jobs.by_source).reduce((a, b) => a + b, 0)}
        icon={<Briefcase className="h-5 w-5" />}
      />
      <MetricCard
        index={1}
        label="Pending Variants"
        value={metrics.variants.pending}
        icon={<Layers className="h-5 w-5" />}
      />
      <MetricCard
        index={2}
        label="Applications Today"
        value={metrics.applications.sent_today}
        icon={<Send className="h-5 w-5" />}
      />
      <MetricCard
        index={3}
        label="Total Sent"
        value={metrics.applications.total}
        icon={<Clock className="h-5 w-5" />}
      />
    </div>
  );
}
