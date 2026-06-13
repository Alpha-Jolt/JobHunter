"use client";

import { useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/shared/state/authStore";
import { authApi } from "@/shared/api/gateway";
import { setAccessToken } from "@/shared/api/client";
import client from "@/shared/api/client";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const attempted = useRef(false);
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated || attempted.current) return;
    attempted.current = true;

    // Attempt silent refresh using the httpOnly refresh cookie
    client
      .post<{ access_token: string }>("/api/auth/refresh")
      .then(async (res) => {
        setAccessToken(res.data.access_token);
        const user = await authApi.me();
        setAuth(user, res.data.access_token);
      })
      .catch(() => {
        clearAuth();
        router.replace("/login");
      });
  }, [isAuthenticated, setAuth, clearAuth, router]);

  return <>{children}</>;
}
