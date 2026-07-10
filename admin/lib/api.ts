import axios from "axios";
import { useAuthStore } from "@/features/auth/authStore";

export const api = axios.create({
  baseURL: "/api",
  withCredentials: true,
});

// Add access token to requests
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
let isRefreshing = false;
let failedQueue: any[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url === "/auth/refresh") {
        window.location.href = "/login";
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers["Authorization"] = "Bearer " + token;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { data } = await api.post("/auth/refresh");
        useAuthStore.getState().setAccessToken(data.access_token);
        originalRequest.headers["Authorization"] = "Bearer " + data.access_token;
        processQueue(null, data.access_token);
        return api(originalRequest);
      } catch (err) {
        processQueue(err, null);
        window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

// ── Company Discovery API ────────────────────────────────────────────────────

export interface StartDiscoveryParams {
  role: string;
  location: string;
  experience?: string;
  salary?: string;
}

export interface BootstrapParams {
  sources?: string[];
}

export interface CompanyListParams {
  crawl_status?: string;
  ats_platform?: string;
  limit?: number;
  offset?: number;
}

export const companyDiscoveryApi = {
  startDiscovery: (params: StartDiscoveryParams) =>
    api.post("/company-discovery/start", params),

  runBootstrap: (params: BootstrapParams = {}) =>
    api.post("/company-discovery/bootstrap", { sources: params.sources ?? ["all"] }),

  getStatus: (runId: string) =>
    api.get(`/company-discovery/status/${runId}`),

  getCompanies: (params: CompanyListParams) =>
    api.get("/company-discovery/companies", { params }),

  getStats: () =>
    api.get("/company-discovery/stats"),
};

// ── Career Jobs API ──────────────────────────────────────────────────────────

export interface JobListParams {
  company_id?: string;
  status?: string;
  limit?: number;
  offset?: number;
}

export const careerJobsApi = {
  startScrape: (companyId?: string) =>
    api.post("/career-jobs/start", { company_id: companyId ?? null }),

  getStatus: (runId: string) =>
    api.get(`/career-jobs/status/${runId}`),

  getLatest: (params: JobListParams = {}) =>
    api.get("/career-jobs/latest", { params }),

  getCounts: () =>
    api.get("/career-jobs/counts"),
};
