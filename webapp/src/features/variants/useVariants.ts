"use client";

import { useEffect, useCallback } from "react";
import { variantsApi } from "@/shared/api/gateway";
import { useVariantStore } from "@/shared/state/variantStore";
import { useAuthStore } from "@/shared/state/authStore";
import { useUiStore } from "@/shared/state/uiStore";

export function useVariants() {
  const { user } = useAuthStore();
  const { allVariants, pendingVariants, isLoading, error, setAll, updateVariantStatus, setLoading, setError } =
    useVariantStore();
  const { addToast } = useUiStore();

  const fetchAll = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    try {
      const data = await variantsApi.all(user.user_id);
      setAll(data.variants);
    } catch {
      setError("Failed to load variants.");
    } finally {
      setLoading(false);
    }
  }, [user, setAll, setLoading, setError]);

  const generate = useCallback(
    async (jobId: string, resumeKey: string): Promise<boolean> => {
      if (!user) return false;
      setLoading(true);
      try {
        const data = await variantsApi.generate(user.user_id, jobId, resumeKey);
        addToast("success", `Variant generated for ${data.job_title}. Review and approve it.`);
        await fetchAll();
        return true;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Variant generation failed.";
        addToast("error", msg);
        return false;
      } finally {
        setLoading(false);
      }
    },
    [user, fetchAll, setLoading, addToast]
  );

  const approve = useCallback(
    async (variantId: string): Promise<boolean> => {
      try {
        const { approval_token } = await variantsApi.getToken(variantId);
        await variantsApi.approve(variantId, approval_token);
        updateVariantStatus(variantId, "approved");
        addToast("success", "Variant approved. You can now send the application.");
        return true;
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : "Approval failed.";
        addToast("error", msg);
        return false;
      }
    },
    [updateVariantStatus, addToast]
  );

  const reject = useCallback(
    async (variantId: string): Promise<boolean> => {
      try {
        await variantsApi.reject(variantId);
        updateVariantStatus(variantId, "rejected");
        addToast("info", "Variant rejected.");
        return true;
      } catch {
        addToast("error", "Rejection failed.");
        return false;
      }
    },
    [updateVariantStatus, addToast]
  );

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  return { allVariants, pendingVariants, isLoading, error, generate, approve, reject, refetch: fetchAll };
}
