import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { config } from "@/lib/config";
import { parseApiError, UnauthorizedError } from "./errors";

let _accessToken: string | null = null;
let _isRefreshing = false;
let _refreshQueue: Array<(token: string | null) => void> = [];

export function setAccessToken(token: string | null): void {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

const client = axios.create({
  baseURL: config.apiBaseUrl,
  timeout: 30_000,
  withCredentials: true, // sends httpOnly refresh cookie automatically
  headers: { "Content-Type": "application/json" },
});

// Attach access token to every request
client.interceptors.request.use((req: InternalAxiosRequestConfig) => {
  if (_accessToken) {
    req.headers["Authorization"] = `Bearer ${_accessToken}`;
  }
  return req;
});

// Handle 401 → refresh → retry
client.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status !== 401 || original._retry) {
      const status = error.response?.status ?? 0;
      const data = error.response?.data;
      throw parseApiError(status, data);
    }

    // Skip refresh loop for auth endpoints themselves
    if (original.url?.includes("/api/auth/")) {
      throw new UnauthorizedError();
    }

    if (_isRefreshing) {
      return new Promise((resolve, reject) => {
        _refreshQueue.push((token) => {
          if (!token) return reject(new UnauthorizedError());
          original._retry = true;
          original.headers["Authorization"] = `Bearer ${token}`;
          resolve(client(original));
        });
      });
    }

    original._retry = true;
    _isRefreshing = true;

    try {
      const { data } = await client.post<{ access_token: string }>("/api/auth/refresh");
      const newToken = data.access_token;
      setAccessToken(newToken);
      _refreshQueue.forEach((cb) => cb(newToken));
      _refreshQueue = [];
      original.headers["Authorization"] = `Bearer ${newToken}`;
      return client(original);
    } catch {
      setAccessToken(null);
      _refreshQueue.forEach((cb) => cb(null));
      _refreshQueue = [];
      throw new UnauthorizedError();
    } finally {
      _isRefreshing = false;
    }
  }
);

export default client;
