import { create } from "zustand";

interface UserProfileState {
  resumeKey: string | null;       // MinIO s3_key of uploaded resume
  resumeFileName: string | null;
  isLoading: boolean;
  error: string | null;
}

interface UserProfileActions {
  setResume: (key: string, fileName: string) => void;
  clearResume: () => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
}

export const useUserProfileStore = create<UserProfileState & UserProfileActions>((set) => ({
  resumeKey: null,
  resumeFileName: null,
  isLoading: false,
  error: null,

  setResume: (key, fileName) => set({ resumeKey: key, resumeFileName: fileName }),
  clearResume: () => set({ resumeKey: null, resumeFileName: null }),
  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
}));
