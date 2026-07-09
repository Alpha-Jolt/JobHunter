import { create } from "zustand";
import type { VariantSummary } from "@/shared/api/types";

interface VariantState {
  pendingVariants: VariantSummary[];
  isLoading: boolean;
  error: string | null;
}

interface VariantActions {
  setPending: (variants: VariantSummary[]) => void;
  removeVariant: (variantId: string) => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
}

export const useVariantStore = create<VariantState & VariantActions>((set) => ({
  pendingVariants: [],
  isLoading: false,
  error: null,

  setPending: (variants) => set({ pendingVariants: variants }),
  removeVariant: (id) =>
    set((s) => ({ pendingVariants: s.pendingVariants.filter((v) => v.variant_id !== id) })),
  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
}));
