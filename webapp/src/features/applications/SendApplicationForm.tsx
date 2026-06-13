"use client";

import { useState } from "react";
import { applicationsApi } from "@/shared/api/gateway";
import { useAuthStore } from "@/shared/state/authStore";
import { useUiStore } from "@/shared/state/uiStore";
import { useForm } from "@/shared/hooks/useForm";
import { sendApplicationSchema, type SendApplicationInput } from "@/shared/utils/validation";
import { Input } from "@/shared/components/Input";
import { Button } from "@/shared/components/Button";
import { ApiError } from "@/shared/api/errors";

interface SendApplicationFormProps {
  jobId: string;
  variantId: string;
  onSuccess?: () => void;
}

export function SendApplicationForm({ jobId, variantId, onSuccess }: SendApplicationFormProps) {
  const { user } = useAuthStore();
  const { addToast } = useUiStore();
  const [isLoading, setIsLoading] = useState(false);

  const { values, errors, handleChange, validate } = useForm<SendApplicationInput>({
    user_name: [user?.first_name, user?.last_name].filter(Boolean).join(" "),
    user_email: user?.email ?? "",
    user_phone: "",
    user_summary: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate(sendApplicationSchema) || !user) return;
    setIsLoading(true);
    try {
      await applicationsApi.send({
        user_id: user.user_id,
        job_id: jobId,
        variant_id: variantId,
        ...values,
      });
      addToast("success", "Application sent successfully!");
      onSuccess?.();
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Failed to send application.";
      addToast("error", msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4" noValidate>
      <Input
        label="Full name"
        name="user_name"
        value={values.user_name}
        onChange={handleChange}
        error={errors.user_name}
        required
      />
      <Input
        label="Email"
        type="email"
        name="user_email"
        value={values.user_email}
        onChange={handleChange}
        error={errors.user_email}
        required
      />
      <Input
        label="Phone"
        type="tel"
        name="user_phone"
        value={values.user_phone}
        onChange={handleChange}
        error={errors.user_phone}
        required
      />
      <div className="flex flex-col gap-1.5">
        <label className="text-sm font-medium text-foreground">Summary</label>
        <textarea
          name="user_summary"
          value={values.user_summary}
          onChange={handleChange}
          rows={3}
          placeholder="Brief introduction for the hiring manager…"
          className="w-full rounded-md border border-input-border bg-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-none"
        />
        {errors.user_summary && (
          <p className="text-xs text-destructive">{errors.user_summary}</p>
        )}
      </div>
      <Button type="submit" isLoading={isLoading} className="w-full">
        Send Application
      </Button>
    </form>
  );
}
