"use client";

import { MapPin, Building2, Check } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";
import { Badge } from "@/shared/components/Badge";
import { truncate, formatRelative, cn } from "@/shared/utils/cn";
import type { JobRecord } from "@/shared/api/types";

interface JobCardProps {
  job: JobRecord;
  onSelect: (job: JobRecord) => void;
  isSelected?: boolean;
}

const trustVariant = {
  verified: "success",
  low: "warning",
  unknown: "outline",
} as const;

export function JobCard({ job, onSelect, isSelected = false }: JobCardProps) {
  return (
    <motion.div whileHover={{ y: -2 }} transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}>
      <Card
        className={cn(
          "cursor-pointer relative overflow-hidden h-full",
          isSelected && "border-ember shadow-[0_0_0_1px_var(--ember)]"
        )}
        onClick={() => onSelect(job)}
      >
        {isSelected && (
          <div className="absolute top-3 right-3 h-6 w-6 rounded-full bg-ember text-paper flex items-center justify-center">
            <Check className="h-3.5 w-3.5" strokeWidth={3} />
          </div>
        )}
        <CardHeader>
          <div className="flex items-start justify-between gap-2 pr-6">
            <div className="flex-1 min-w-0">
              <CardTitle className="truncate">{job.title}</CardTitle>
              <div className="flex items-center gap-2 mt-1.5 text-sm text-foreground-muted">
                <Building2 className="h-3.5 w-3.5 shrink-0 opacity-70" />
                <span className="truncate">{job.company_name}</span>
              </div>
            </div>
            <Badge variant={trustVariant[job.email_trust]}>{job.email_trust}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {job.location && (
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground mb-2.5">
              <MapPin className="h-3.5 w-3.5" />
              {job.location}
            </div>
          )}
          <p className="text-sm text-foreground-muted line-clamp-2 mb-3 leading-relaxed">
            {truncate(job.description, 160)}
          </p>
          {job.skills_required.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mb-4">
              {job.skills_required.slice(0, 4).map((s) => (
                <Badge key={s} variant="secondary">
                  {s}
                </Badge>
              ))}
              {job.skills_required.length > 4 && (
                <Badge variant="outline">+{job.skills_required.length - 4}</Badge>
              )}
            </div>
          )}
          <div className="flex items-center justify-between border-t border-border pt-3">
            <span className="font-mono-label text-muted-foreground normal-case tracking-normal">
              {formatRelative(job.created_at)}
            </span>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
