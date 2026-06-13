"use client";

import { useEffect, useState, useCallback } from "react";
import { applicationsApi } from "@/shared/api/gateway";
import { useAuthStore } from "@/shared/state/authStore";
import { formatRelative } from "@/shared/utils/cn";
import { Badge } from "@/shared/components/Badge";
import { Card, CardContent } from "@/shared/components/Card";
import { Skeleton } from "@/shared/components/Skeleton";
import type { ApplicationRecord } from "@/shared/api/types";

const statusVariant: Record<string, "success" | "warning" | "destructive" | "secondary" | "outline"> = {
  sent: "secondary",
  replied: "success",
  interview_scheduled: "success",
  rejected: "destructive",
  ghosted: "outline",
};

export function ApplicationHistory() {
  const { user } = useAuthStore();
  const [apps, setApps] = useState<ApplicationRecord[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const load = useCallback(async () => {
    if (!user) return;
    setIsLoading(true);
    try {
      const data = await applicationsApi.sentToday(user.user_id);
      setApps(data.applications);
    } catch {
      // silent — page still renders empty state
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => { load(); }, [load]);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
      </div>
    );
  }

  if (!apps.length) {
    return (
      <div className="text-center py-12 text-muted-foreground text-sm">
        No applications sent today.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      {apps.map((app) => (
        <Card key={app.application_id}>
          <CardContent className="pt-4 flex items-center justify-between gap-4">
            <div className="min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                Application #{app.application_id.slice(0, 8)}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {formatRelative(app.sent_at)}
              </p>
            </div>
            <Badge variant={statusVariant[app.status] ?? "secondary"}>
              {app.status.replace("_", " ")}
            </Badge>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
