import client from "./client";
import type {
  AuthResponse,
  RegisterPayload,
  LoginPayload,
  JobRecord,
  ResumeUploadResponse,
  GenerateVariantResponse,
  PendingVariantsResponse,
  PreviewVariantResponse,
  ApproveVariantResponse,
  ApplicationRecord,
  SendApplicationPayload,
  SendApplicationResponse,
  SentTodayResponse,
  DashboardMetrics,
} from "./types";

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  register: (payload: RegisterPayload) =>
    client.post<AuthResponse>("/api/auth/register", payload).then((r) => r.data),

  login: (payload: LoginPayload) =>
    client.post<AuthResponse>("/api/auth/login", payload).then((r) => r.data),

  me: () =>
    client.get<{ user: AuthResponse["user"] }>("/api/auth/me").then((r) => r.data.user),

  logout: () => client.post<{ success: boolean }>("/api/auth/logout").then((r) => r.data),

  changePassword: (current_password: string, new_password: string) =>
    client
      .patch<{ success: boolean }>("/api/auth/me/password", { current_password, new_password })
      .then((r) => r.data),
};

// ── Jobs ──────────────────────────────────────────────────────────────────────

export const jobsApi = {
  list: (params?: { source?: string; limit?: number; offset?: number }) =>
    client
      .get<{ jobs: JobRecord[]; total?: number }>("/api/scraper/latest-jobs", { params })
      .then((r) => r.data),

  counts: () =>
    client.get<Record<string, unknown>>("/api/scraper/counts").then((r) => r.data),
};

// ── Resume ────────────────────────────────────────────────────────────────────

export const resumeApi = {
  upload: (file: File, userId: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("user_id", userId);
    return client
      .post<ResumeUploadResponse>("/api/resume/upload", form, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },
};

// ── Variants ──────────────────────────────────────────────────────────────────

export const variantsApi = {
  generate: (user_id: string, job_id: string, resume_file_path: string) =>
    client
      .post<GenerateVariantResponse>("/api/ai/generate", {
        user_id,
        job_id,
        resume_file_path,
      })
      .then((r) => r.data),

  pending: (userId: string) =>
    client
      .get<PendingVariantsResponse>(`/api/ai/pending/${userId}`)
      .then((r) => r.data),

  preview: (variantId: string) =>
    client
      .get<PreviewVariantResponse>(`/api/ai/preview/${variantId}`)
      .then((r) => r.data),

  approve: (variantId: string, token: string) =>
    client
      .post<ApproveVariantResponse>(`/api/ai/approve/${variantId}?token=${encodeURIComponent(token)}`)
      .then((r) => r.data),

  reject: (variantId: string, user_feedback?: string) =>
    client
      .post(`/api/ai/reject/${variantId}`, { user_feedback })
      .then((r) => r.data),
};

// ── Applications ──────────────────────────────────────────────────────────────

export const applicationsApi = {
  send: (payload: SendApplicationPayload) =>
    client.post<SendApplicationResponse>("/api/mail/send", payload).then((r) => r.data),

  status: (applicationId: string) =>
    client
      .get<ApplicationRecord>(`/api/mail/status/${applicationId}`)
      .then((r) => r.data),

  sentToday: (userId: string) =>
    client.get<SentTodayResponse>(`/api/mail/sent-today/${userId}`).then((r) => r.data),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────

export const dashboardApi = {
  metrics: () =>
    client.get<DashboardMetrics>("/api/admin/dashboard/metrics").then((r) => r.data),
};
