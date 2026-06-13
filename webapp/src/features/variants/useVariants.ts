"use client";

import { useEffect, useCallback } from "react";
import { variantsApi } from "@/shared/api/gateway";
import { useVariantStore, saveVariantToken } from "@/shared/state/variantStore";
import { useAuthStore } from "@/shared/state/authStore";
import { useUiStore } from "@/shared/state/uiStore";

export function useVariants() {
  const { user } = useAuthStore();
  const { pendingVariants, isLoading, error, setPending, setLoading, setError } = useVariantStore();
  const { addToast } = useUiStore();

  const fetchPending = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await variantsApi.pending(user.user_id);
      setPending(data.pending);
    } catch {
      setError("Failed to load variants.");
    } finally {
      setLoading(false);
    }
  }, [user, setPending, setLoading, setError]);

  const generate = useCallback(
    async (jobId: string, resumeKey: string): Promise<boolean> => {
      if (!user) return false;
      setLoading(true);
      try {
        const data = await variantsApi.generate(user.user_id, jobId, resumeKey);
        // Securely store token in sessionStorage immediately after generation
        saveVariantToken(data.variant_id, data.approval_token);
        addToast("success", `Variant generated for ${data.job_title}. Review and approve it.`);
        await fetchPending();
        return true;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Variant generation failed.";
        addToast("error", msg);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [user, fetchPending, setLoading, addToast]
  );

  useEffect(() => {
    fetchPending();
  }, [fetchPending]);

  return { pendingVariants, isLoading, error, generate, refetch: fetchPending };
}
