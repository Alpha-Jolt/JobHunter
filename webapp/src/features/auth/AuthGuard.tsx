"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/shared/state/authStore";
import { useUserProfileStore } from "@/shared/state/userProfileStore";
import { useProfileStore } from "@/shared/state/profileStore";
import { authApi, profileApi } from "@/shared/api/gateway";
import { setAccessToken } from "@/shared/api/client";
import client from "@/shared/api/client";
import { Loader2 } from "lucide-react";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, setAuth, clearAuth } = useAuthStore();
  const { setResume } = useUserProfileStore();
  const { profile, setProfile } = useProfileStore();
  const [isInitializing, setIsInitializing] = useState(!isAuthenticated);
  const attempted = useRef(false);
  const router = useRouter();

  useEffect(() => {
    if (isAuthenticated || attempted.current) {
      setIsInitializing(false);
      return;
    }
    attempted.current = true;

    // Attempt silent refresh using the httpOnly refresh cookie
    client
      .post<{ access_token: string }>("/api/auth/refresh")
      .then(async (res) => {
        setAccessToken(res.data.access_token);
        const user = await authApi.me();
        setAuth(user, res.data.access_token);
        if (user.resume) {
          setResume(user.resume.resumeKey, user.resume.resumeFileName);
        }
      })
      .catch(() => {
        clearAuth();
        router.replace("/login");
      })
      .finally(() => {
        setIsInitializing(false);
      });
  }, [isAuthenticated, setAuth, clearAuth, router, setResume]);

  // Global fetch for profile
  useEffect(() => {
    if (isAuthenticated && !profile) {
      profileApi.getMe()
        .then((data) => setProfile(data))
        .catch(() => {
          // It's okay if profile doesn't exist yet (404)
        });
    }
  }, [isAuthenticated, profile, setProfile]);

  if (isInitializing) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated && attempted.current) {
    return null;
  }

  return <>{children}</>;
}
