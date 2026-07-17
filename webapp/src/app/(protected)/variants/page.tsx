"use client";

import { useVariants } from "@/features/variants/useVariants";
import { VariantCard } from "@/features/variants/VariantCard";
import { Skeleton } from "@/shared/components/Skeleton";

export default function VariantsPage() {
  const { allVariants, isLoading, approve, reject } = useVariants();

  const pending  = allVariants.filter((v) => v.approval_status === "pending");
  const approved = allVariants.filter((v) => v.approval_status === "approved");
  const rejected = allVariants.filter((v) => v.approval_status === "rejected");

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Variants</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Review AI-tailored resumes before sending. Nothing sends without your approval.
        </p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2].map((i) => <Skeleton key={i} className="h-52" />)}
        </div>
      ) : allVariants.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground text-sm">
          No variants yet. Go to Jobs to generate one.
        </div>
      ) : (
        <div className="flex flex-col gap-8">
          {/* Pending */}
          {pending.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-foreground mb-3">
                Awaiting Review ({pending.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {pending.map((v) => (
                  <VariantCard key={v.variant_id} variant={v} onApprove={approve} onReject={reject} />
                ))}
              </div>
            </section>
          )}

          {/* Approved */}
          {approved.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-green-600 dark:text-green-400 mb-3">
                Approved ({approved.length})
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {approved.map((v) => (
                  <VariantCard key={v.variant_id} variant={v} onApprove={approve} onReject={reject} />
                ))}
              </div>
            </section>
          )}

          {/* Rejected */}
          {rejected.length > 0 && (
            <section>
              <h2 className="text-sm font-semibold text-muted-foreground mb-3">
                Rejected ({rejected.length})
              </h2>
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
