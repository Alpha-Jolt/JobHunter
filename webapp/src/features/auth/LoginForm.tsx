"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "@/shared/hooks/useForm";
import { loginSchema, type LoginInput } from "@/shared/utils/validation";
import { authApi } from "@/shared/api/gateway";
import { useAuthStore } from "@/shared/state/authStore";
import { useUiStore } from "@/shared/state/uiStore";
import { Input } from "@/shared/components/Input";
import { Button } from "@/shared/components/Button";
import { ApiError } from "@/shared/api/errors";

export function LoginForm() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const { addToast } = useUiStore();
  const [isLoading, setIsLoading] = useState(false);
  const { values, errors, handleChange, validate } = useForm<LoginInput>({
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate(loginSchema)) return;
    setIsLoading(true);
    try {
      const data = await authApi.login(values);
      setAuth(data.user, data.access_token);
      router.replace("/dashboard");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Login failed.";
      addToast("error", msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <Input
        label="Email"
        type="email"
        name="email"
        autoComplete="email"
        value={values.email}
        onChange={handleChange}
        error={errors.email}
        required
      />
      <Input
        label="Password"
        type="password"
        name="password"
        autoComplete="current-password"
        value={values.password}
        onChange={handleChange}
        error={errors.password}
        required
      />
      <Button type="submit" isLoading={isLoading} className="w-full mt-2">
        Sign in
      </Button>
    </form>
  );
}
