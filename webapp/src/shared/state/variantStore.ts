import { create } from "zustand";
import type { VariantSummary } from "@/shared/api/types";
import type { VariantSummaryFull } from "@/shared/api/gateway";

interface VariantState {
  pendingVariants: VariantSummary[];
  allVariants: VariantSummaryFull[];
  isLoading: boolean;
  error: string | null;
}

interface VariantActions {
  setPending: (variants: VariantSummary[]) => void;
  setAll: (variants: VariantSummaryFull[]) => void;
  updateVariantStatus: (variantId: string, status: "approved" | "rejected") => void;
  removeVariant: (variantId: string) => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
}

export const useVariantStore = create<VariantState & VariantActions>((set) => ({
  pendingVariants: [],
  allVariants: [],
  isLoading: false,
  error: null,

  setPending: (variants) => set({ pendingVariants: variants }),

  setAll: (variants) =>
    set({
      allVariants: variants,
      pendingVariants: variants.filter((v) => v.approval_status === "pending"),
    }),

  updateVariantStatus: (id, status) =>
    set((s) => ({
      allVariants: s.allVariants.map((v) =>
        v.variant_id === id ? { ...v, approval_status: status } : v
      ),
      pendingVariants: s.pendingVariants.filter((v) => v.variant_id !== id),
    })),

  // Keep for backward compat — just drops from pending list
  removeVariant: (id) =>
    set((s) => ({
      pendingVariants: s.pendingVariants.filter((v) => v.variant_id !== id),
      allVariants: s.allVariants.filter((v) => v.variant_id !== id),
    })),

  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
}));
