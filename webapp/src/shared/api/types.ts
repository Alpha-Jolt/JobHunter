// ── Auth ──────────────────────────────────────────────────────────────────────

export interface UserRecord {
  user_id: string;
  email: string;
  role: "hunter" | "mentor" | "recruiter" | "admin";
  first_name: string | null;
  last_name: string | null;
  is_active: boolean;
  is_verified: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserRecord;
}

export interface RegisterPayload {
  email: string;
  password: string;
  role: "hunter" | "mentor" | "recruiter" | "admin";
  first_name?: string;
  last_name?: string;
  phone?: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

// ── Jobs ──────────────────────────────────────────────────────────────────────

export interface JobRecord {
  job_id: string;
  source: string;
  title: string;
  company_name: string;
  location: string | null;
  description: string;
  skills_required: string[];
  apply_email: string | null;
  email_trust: "unknown" | "verified" | "low";
  status: "raw" | "reviewed" | "applied" | "closed";
  last_seen_at: string | null;
  created_at: string;
}

export interface JobsResponse {
  jobs: JobRecord[];
  total: number;
  offset: number;
  limit: number;
}

// ── Resume ────────────────────────────────────────────────────────────────────

export interface ResumeUploadResponse {
  s3_key: string;
  file_name: string;
}

// ── Variants ──────────────────────────────────────────────────────────────────

export interface VariantSummary {
  variant_id: string;
  job_id: string;
  job_title: string;
  company_name: string;
  match_score: number;
  created_at: string | null;
  approval_link: string;
}

export interface GenerateVariantResponse {
  variant_id: string;
  approval_token: string;
  job_title: string;
  company_name: string;
  match_score: number;
  created_at: string | null;
  status: string;
  approval_link: string;
}

export interface PendingVariantsResponse {
  total: number;
  pending: VariantSummary[];
}

export interface PreviewVariantResponse {
  variant_id: string;
  approval_status: string;
  curated_resume: Record<string, unknown>;
  gaps: string[];
  match_score: number;
}

export interface ApproveVariantResponse {
  variant_id: string;
  status: string;
  approved_at: string | null;
  message: string;
}

// ── Applications ──────────────────────────────────────────────────────────────

export interface ApplicationRecord {
  application_id: string;
  user_id: string;
  job_id: string;
  status: "sent" | "replied" | "interview_scheduled" | "rejected" | "ghosted";
  sent_at: string;
  reply_count: number;
}

export interface SendApplicationPayload {
  user_id: string;
  job_id: string;
  variant_id: string;
  user_name: string;
  user_email: string;
  user_phone: string;
  user_summary: string;
}

export interface SendApplicationResponse {
  success: boolean;
  application_id: string;
  message_id: string;
  sent_at: string;
}

export interface SentTodayResponse {
  count: number;
  applications: ApplicationRecord[];
}

// ── Dashboard ─────────────────────────────────────────────────────────────────

export interface DashboardMetrics {
  timestamp: string;
  jobs: {
    total: number;
    by_source: Record<string, number>;
  };
  variants: {
    total: number;
    pending: number;
    approved: number;
  };
  applications: {
    total: number;
    sent_today: number;
  };
  scraper: {
    last_run: string | null;
    last_status: string;
  };
}
