"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, Eye } from "lucide-react";
import { variantsApi } from "@/shared/api/gateway";
import { useVariantStore } from "@/shared/state/variantStore";
import { useUiStore } from "@/shared/state/uiStore";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";
import { Button } from "@/shared/components/Button";
import { Badge } from "@/shared/components/Badge";
import { config } from "@/lib/config";
import { getAccessToken } from "@/shared/api/client";
import type { VariantSummary, PreviewVariantResponse } from "@/shared/api/types";

interface VariantCardProps {
  variant: VariantSummary;
}

export function VariantCard({ variant }: VariantCardProps) {
  const { removeVariant } = useVariantStore();
  const { addToast } = useUiStore();
  const [preview, setPreview] = useState<PreviewVariantResponse | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);

  const loadPreview = async () => {
    if (preview) { setShowPreview(true); return; }
    setIsLoadingPreview(true);
    try {
      const data = await variantsApi.preview(variant.variant_id);
      setPreview(data);
      setShowPreview(true);
    } catch {
      addToast("error", "Failed to load preview.");
    } finally {
      setIsLoadingPreview(false);
    }
  };

  const handleApprove = async () => {
    setIsApproving(true);
    try {
      // Fetch token from server on demand — never stored persistently
      const { approval_token } = await variantsApi.getToken(variant.variant_id);
      await variantsApi.approve(variant.variant_id, approval_token);
      removeVariant(variant.variant_id);
      addToast("success", "Variant approved. You can now send the application.");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Approval failed.";
      addToast("error", msg);
    } finally {
      setIsApproving(false);
    }
  };

  const handleReject = async () => {
    setIsRejecting(true);
    try {
      await variantsApi.reject(variant.variant_id);
      removeVariant(variant.variant_id);
      addToast("info", "Variant rejected.");
    } catch {
      addToast("error", "Rejection failed.");
    } finally {
      setIsRejecting(false);
    }
  };

  const handleDownload = (format: string, action: "download" | "preview" = "download") => {
    const url = `${config.apiBaseUrl}/api/ai/download/${variant.variant_id}?format=${format}`;
    const token = getAccessToken();
    
    fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    .then(res => {
      if (!res.ok) throw new Error("File not available");
      return res.blob();
    })
    .then(blob => {
      const blobUrl = window.URL.createObjectURL(blob);
      if (action === "preview" && format === "pdf") {
        window.open(blobUrl, "_blank");
        // We can't immediately revoke the URL if it's opened in a new tab,
        // so we leave it to be garbage collected when the tab closes.
      } else {
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = `Resume_${variant.variant_id}.${format}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
      }
    })
    .catch(() => {
      addToast("error", "Failed to " + action + " " + format.toUpperCase());
    });
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "bg-green-500";
    if (score >= 60) return "bg-yellow-500";
    if (score >= 45) return "bg-orange-500";
    return "bg-red-500";
  };
  
  const getTextColor = (score: number) => {
    if (score >= 80) return "text-green-600 dark:text-green-400";
    if (score >= 60) return "text-yellow-600 dark:text-yellow-400";
    if (score >= 45) return "text-orange-600 dark:text-orange-400";
    return "text-red-600 dark:text-red-400";
  };
  
  const getScoreLabel = (score: number) => {
    if (score >= 80) return "High Match";
    if (score >= 60) return "Medium Match";
    if (score >= 45) return "Low Match";
    return "Poor Match";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle>{variant.job_title}</CardTitle>
            <p className="text-sm text-muted-foreground mt-0.5">{variant.company_name}</p>
          </div>
          <Badge variant="warning">Pending</Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mb-1">
          <span className={`text-xs font-semibold ${getTextColor(variant.match_score)}`}>
            {getScoreLabel(variant.match_score)}
          </span>
          <span className={`text-xs font-medium w-10 text-right ${getTextColor(variant.match_score)}`}>
            {Math.round(variant.match_score)}%
          </span>
        </div>
        <div className="flex items-center gap-2 mb-4">
          <div className="flex-1 h-2 rounded-full bg-secondary overflow-hidden">
            <div
              className={`h-2 rounded-full transition-all ${getScoreColor(variant.match_score)}`}
              style={{ width: `${Math.min(Math.round(variant.match_score), 100)}%` }}
            />
          </div>
        </div>

        {/* Preview panel */}
        {showPreview && preview && (
          <div className="mb-3 p-3 rounded-md bg-background-subtle border border-border text-xs max-h-48 overflow-y-auto">
            {preview.gaps.length > 0 && (
              <div className="mb-2">
                <p className="font-medium text-foreground mb-1">Skill gaps:</p>
                <ul className="list-disc list-inside text-muted-foreground space-y-0.5">
                  {preview.gaps.map((g) => <li key={g}>{g}</li>)}
                </ul>
              </div>
            )}
            <p className="text-muted-foreground">
              {preview.curated_resume["summary"] as string ?? "Preview loaded."}
            </p>
          </div>
        )}

        {/* Preview panel */}

        <div className="flex gap-2 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={loadPreview}
            isLoading={isLoadingPreview}
          >
            <Eye className="h-3.5 w-3.5" />
            {showPreview ? "Hide" : "Preview"}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDownload("docx")}
          >
            DOCX
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDownload("pdf", "download")}
          >
            PDF
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleDownload("pdf", "preview")}
          >
            Preview PDF
          </Button>
          <Button
            size="sm"
            onClick={handleApprove}
            isLoading={isApproving}
          >
            <CheckCircle2 className="h-3.5 w-3.5" />
            Approve
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={handleReject}
            isLoading={isRejecting}
          >
            <XCircle className="h-3.5 w-3.5" />
            Reject
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
