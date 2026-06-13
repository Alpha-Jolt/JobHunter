import { DashboardMetricsGrid } from "@/features/dashboard/DashboardMetrics";
import Link from "next/link";
import { Button } from "@/shared/components/Button";
import { Briefcase, FileText, Layers } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Your job hunt at a glance.</p>
      </div>

      <DashboardMetricsGrid />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Link href="/jobs">
          <Button variant="outline" className="w-full justify-start gap-3 h-14">
            <Briefcase className="h-5 w-5 text-primary" />
            Browse Jobs
          </Button>
        </Link>
        <Link href="/resume">
          <Button variant="outline" className="w-full justify-start gap-3 h-14">
            <FileText className="h-5 w-5 text-primary" />
            Manage Resume
          </Button>
        </Link>
        <Link href="/variants">
          <Button variant="outline" className="w-full justify-start gap-3 h-14">
            <Layers className="h-5 w-5 text-primary" />
            Review Variants
          </Button>
        </Link>
      </div>
    </div>
  );
}
