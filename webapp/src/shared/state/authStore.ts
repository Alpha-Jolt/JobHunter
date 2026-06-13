import { create } from "zustand";
import { setAccessToken } from "@/shared/api/client";
import type { UserRecord } from "@/shared/api/types";

interface AuthState {
  user: UserRecord | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  setAuth: (user: UserRecord, token: string) => void;
  clearAuth: () => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
}

export const useAuthStore = create<AuthState & AuthActions>((set) => ({
  user: null,
  accessToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  setAuth: (user, token) => {
    setAccessToken(token);
    set({ user, accessToken: token, isAuthenticated: true, error: null });
  },

  clearAuth: () => {
    setAccessToken(null);
    // Clear all variant approval tokens from sessionStorage
    if (typeof window !== "undefined") {
      Object.keys(sessionStorage)
        .filter((k) => k.startsWith("jh_vt_"))
        .forEach((k) => sessionStorage.removeItem(k));
    }
    set({ user: null, accessToken: null, isAuthenticated: false });
  },

  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
}));
