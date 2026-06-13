"use client";

import { MapPin, Building2, Zap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";
import { Badge } from "@/shared/components/Badge";
import { Button } from "@/shared/components/Button";
import { truncate, formatRelative } from "@/shared/utils/cn";
import type { JobRecord } from "@/shared/api/types";

interface JobCardProps {
  job: JobRecord;
  onSelect: (job: JobRecord) => void;
}

const trustVariant = {
  verified: "success",
  low: "warning",
  unknown: "outline",
} as const;

export function JobCard({ job, onSelect }: JobCardProps) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <CardTitle className="truncate">{job.title}</CardTitle>
            <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
              <Building2 className="h-3.5 w-3.5 shrink-0" />
              <span className="truncate">{job.company_name}</span>
            </div>
          </div>
          <Badge variant={trustVariant[job.email_trust]}>
            {job.email_trust}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        {job.location && (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2">
            <MapPin className="h-3.5 w-3.5" />
            {job.location}
          </div>
        )}
        <p className="text-sm text-foreground-muted line-clamp-2 mb-3">
          {truncate(job.description, 160)}
        </p>
        {job.skills_required.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {job.skills_required.slice(0, 4).map((s) => (
              <Badge key={s} variant="secondary">{s}</Badge>
            ))}
            {job.skills_required.length > 4 && (
              <Badge variant="outline">+{job.skills_required.length - 4}</Badge>
            )}
          </div>
        )}
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">{formatRelative(job.created_at)}</span>
          <Button size="sm" onClick={() => onSelect(job)}>
            <Zap className="h-3.5 w-3.5" />
            Generate Variant
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
