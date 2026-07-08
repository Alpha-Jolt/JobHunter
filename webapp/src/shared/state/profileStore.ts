import { create } from "zustand";
import type { UserProfile } from "../api/types";

interface ProfileState {
  profile: UserProfile | null;
  isLoading: boolean;
  error: string | null;
  setProfile: (profile: UserProfile) => void;
  updateSection: (section: Partial<UserProfile>) => void;
  clearProfile: () => void;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: null,
  isLoading: false,
  error: null,
  setProfile: (profile) => set({ profile, error: null }),
  updateSection: (section) =>
    set((state) => ({
      profile: state.profile ? { ...state.profile, ...section } : null,
    })),
  clearProfile: () => set({ profile: null, error: null }),
}));
