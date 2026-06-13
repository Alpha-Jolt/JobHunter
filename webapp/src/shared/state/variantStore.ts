import { create } from "zustand";
import type { VariantSummary } from "@/shared/api/types";

// Approval token stored in sessionStorage keyed by variant_id.
// The raw token never lives in Zustand memory — only sessionStorage.

const TOKEN_PREFIX = "jh_vt_";

export function saveVariantToken(variantId: string, token: string): void {
  if (typeof window === "undefined") return;
  // Validate 3-part HMAC format before storing
  if (token.split(":").length !== 3) return;
  sessionStorage.setItem(`${TOKEN_PREFIX}${variantId}`, token);
}

export function getVariantToken(variantId: string): string | null {
  if (typeof window === "undefined") return null;
  return sessionStorage.getItem(`${TOKEN_PREFIX}${variantId}`);
}

export function clearVariantToken(variantId: string): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(`${TOKEN_PREFIX}${variantId}`);
}

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
