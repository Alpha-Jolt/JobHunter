"use client";

import { useVariants } from "@/features/variants/useVariants";
import { VariantCard } from "@/features/variants/VariantCard";
import { Skeleton } from "@/shared/components/Skeleton";
import { PageHeader } from "@/shared/components/Motion";

export default function VariantsPage() {
  const { allVariants, isLoading, approve, reject } = useVariants();

  const pending = allVariants.filter((v) => v.approval_status === "pending");
  const approved = allVariants.filter((v) => v.approval_status === "approved");
  const rejected = allVariants.filter((v) => v.approval_status === "rejected");

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        label="Approval queue"
        title="Variants"
        description="Review AI-tailored resumes before sending. Nothing goes out without your approval."
      />

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2].map((i) => (
            <Skeleton key={i} className="h-52 rounded-[var(--radius)]" />
          ))}
        </div>
      ) : allVariants.length === 0 ? (
        <div className="text-center py-20 border border-dashed border-border-strong rounded-[var(--radius)]">
          <p className="font-display text-lg text-foreground">No variants yet</p>
          <p className="text-sm text-muted-foreground mt-2">Go to Jobs to generate your first draft.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-10">
          {pending.length > 0 && (
            <section>
              <p className="section-label">Awaiting review · {pending.length}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pending.map((v) => (
                  <VariantCard key={v.variant_id} variant={v} onApprove={approve} onReject={reject} />
                ))}
              </div>
            </section>
          )}

          {approved.length > 0 && (
            <section>
              <p className="section-label">Approved · {approved.length}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {approved.map((v) => (
                  <VariantCard key={v.variant_id} variant={v} onApprove={approve} onReject={reject} />
                ))}
              </div>
            </section>
          )}

          {rejected.length > 0 && (
            <section>
              <p className="section-label !text-muted-foreground">Rejected · {rejected.length}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {rejected.map((v) => (
                  <VariantCard key={v.variant_id} variant={v} onApprove={approve} onReject={reject} />
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
}
