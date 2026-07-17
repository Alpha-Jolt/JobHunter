"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, Eye } from "lucide-react";
import { variantsApi } from "@/shared/api/gateway";
import { useUiStore } from "@/shared/state/uiStore";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";
import { Button } from "@/shared/components/Button";
import { Badge } from "@/shared/components/Badge";
import { config } from "@/lib/config";
import { getAccessToken } from "@/shared/api/client";
import type { PreviewVariantResponse } from "@/shared/api/types";
import type { VariantSummaryFull } from "@/shared/api/gateway";

interface VariantCardProps {
  variant: VariantSummaryFull;
  onApprove: (variantId: string) => Promise<boolean>;
  onReject: (variantId: string) => Promise<boolean>;
}

const STATUS_BADGE: Record<string, React.ReactNode> = {
  pending:  <Badge variant="warning">Pending</Badge>,
  approved: <Badge variant="success">Approved</Badge>,
  rejected: <Badge variant="destructive">Rejected</Badge>,
};

export function VariantCard({ variant, onApprove, onReject }: VariantCardProps) {
  const { addToast } = useUiStore();
  const [preview, setPreview] = useState<PreviewVariantResponse | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [isLoadingPreview, setIsLoadingPreview] = useState(false);
  const [isApproving, setIsApproving] = useState(false);
  const [isRejecting, setIsRejecting] = useState(false);

  const isPending = variant.approval_status === "pending";

  const loadPreview = async () => {
    if (preview) { setShowPreview((v) => !v); return; }
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
    await onApprove(variant.variant_id);
    setIsApproving(false);
  };

  const handleReject = async () => {
    setIsRejecting(true);
    await onReject(variant.variant_id);
    setIsRejecting(false);
  };

  const handleDownload = (format: string, action: "download" | "preview" = "download") => {
    const url = `${config.apiBaseUrl}/api/ai/download/${variant.variant_id}?format=${format}`;
    const token = getAccessToken();
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error("File not available");
        return res.blob();
      })
      .then((blob) => {
        const blobUrl = window.URL.createObjectURL(blob);
        if (action === "preview" && format === "pdf") {
          window.open(blobUrl, "_blank");
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
      .catch(() => addToast("error", `Failed to ${action} ${format.toUpperCase()}`));
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

  const hasFiles = variant.pdf_key || variant.docx_key;

  return (
    <Card className={variant.approval_status === "rejected" ? "opacity-70" : ""}>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle>{variant.job_title}</CardTitle>
            <p className="text-sm text-muted-foreground mt-0.5">{variant.company_name}</p>
          </div>
          {STATUS_BADGE[variant.approval_status] ?? <Badge variant="outline">{variant.approval_status}</Badge>}
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

        {/* Approved info banner */}
        {variant.approval_status === "approved" && variant.approved_at && (
          <p className="text-xs text-green-600 dark:text-green-400 mb-3">
            ✓ Approved {new Date(variant.approved_at).toLocaleDateString()}
          </p>
        )}

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

        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={loadPreview} isLoading={isLoadingPreview}>
            <Eye className="h-3.5 w-3.5" />
            {showPreview ? "Hide" : "Preview"}
          </Button>

          {hasFiles && (
            <>
              {variant.docx_key && (
                <Button variant="outline" size="sm" onClick={() => handleDownload("docx")}>
                  DOCX
                </Button>
              )}
              {variant.pdf_key && (
                <>
                  <Button variant="outline" size="sm" onClick={() => handleDownload("pdf")}>
                    PDF
                  </Button>
                  <Button variant="outline" size="sm" onClick={() => handleDownload("pdf", "preview")}>
                    Preview PDF
                  </Button>
                </>
              )}
            </>
          )}

          {isPending && (
            <>
              <Button size="sm" onClick={handleApprove} isLoading={isApproving}>
                <CheckCircle2 className="h-3.5 w-3.5" />
                Approve
              </Button>
              <Button variant="destructive" size="sm" onClick={handleReject} isLoading={isRejecting}>
                <XCircle className="h-3.5 w-3.5" />
                Reject
              </Button>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
