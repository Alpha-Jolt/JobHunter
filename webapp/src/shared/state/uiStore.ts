import { create } from "zustand";

interface Toast {
  id: string;
  type: "success" | "error" | "warning" | "info";
  message: string;
}

interface UiState {
  toasts: Toast[];
  sidebarOpen: boolean;
  activeModal: string | null;
}

interface UiActions {
  addToast: (type: Toast["type"], message: string) => void;
  removeToast: (id: string) => void;
  setSidebarOpen: (v: boolean) => void;
  openModal: (name: string) => void;
  closeModal: () => void;
}

export const useUiStore = create<UiState & UiActions>((set) => ({
  toasts: [],
  sidebarOpen: false,
  activeModal: null,

  addToast: (type, message) =>
    set((s) => ({
      toasts: [...s.toasts, { id: crypto.randomUUID(), type, message }],
    })),
  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
  setSidebarOpen: (v) => set({ sidebarOpen: v }),
  openModal: (name) => set({ activeModal: name }),
  closeModal: () => set({ activeModal: null }),
}));
