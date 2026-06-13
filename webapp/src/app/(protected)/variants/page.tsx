"use client";

import { useVariants } from "@/features/variants/useVariants";
import { VariantCard } from "@/features/variants/VariantCard";
import { Skeleton } from "@/shared/components/Skeleton";

export default function VariantsPage() {
  const { pendingVariants, isLoading } = useVariants();

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
      ) : pendingVariants.length === 0 ? (
        <div className="text-center py-16 text-muted-foreground text-sm">
          No pending variants. Go to Jobs to generate one.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {pendingVariants.map((v) => (
            <VariantCard key={v.variant_id} variant={v} />
          ))}
        </div>
      )}
    </div>
  );
}
