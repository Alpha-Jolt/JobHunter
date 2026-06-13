"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "@/shared/hooks/useForm";
import { registerSchema, type RegisterInput } from "@/shared/utils/validation";
import { authApi } from "@/shared/api/gateway";
import { useAuthStore } from "@/shared/state/authStore";
import { useUiStore } from "@/shared/state/uiStore";
import { Input } from "@/shared/components/Input";
import { Button } from "@/shared/components/Button";
import { ApiError } from "@/shared/api/errors";

export function SignupForm() {
  const router = useRouter();
  const { setAuth } = useAuthStore();
  const { addToast } = useUiStore();
  const [isLoading, setIsLoading] = useState(false);
  const { values, errors, handleChange, validate } = useForm<RegisterInput>({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "hunter" as const,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate(registerSchema)) return;
    setIsLoading(true);
    try {
      const data = await authApi.register(values);
      setAuth(data.user, data.access_token);
      router.replace("/dashboard");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Registration failed.";
      addToast("error", msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <div className="grid grid-cols-2 gap-3">
        <Input
          label="First name"
          name="first_name"
          autoComplete="given-name"
          value={values.first_name}
          onChange={handleChange}
          error={errors.first_name}
          required
        />
        <Input
          label="Last name"
          name="last_name"
          autoComplete="family-name"
          value={values.last_name}
          onChange={handleChange}
          error={errors.last_name}
          required
        />
      </div>
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
        autoComplete="new-password"
        value={values.password}
        onChange={handleChange}
        error={errors.password}
        required
      />
      <Button type="submit" isLoading={isLoading} className="w-full mt-2">
        Create account
      </Button>
    </form>
  );
}
