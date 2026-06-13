"use client";

import { useState, useCallback } from "react";
import type { ZodSchema } from "zod";

type Errors<T> = Partial<Record<keyof T, string>>;

export function useForm<T extends Record<string, unknown>>(initial: T) {
  const [values, setValues] = useState<T>(initial);
  const [errors, setErrors] = useState<Errors<T>>({});

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
      const { name, value } = e.target;
      setValues((v) => ({ ...v, [name]: value }));
      setErrors((errs) => ({ ...errs, [name]: undefined }));
    },
    []
  );

  const validate = useCallback(
    (schema: ZodSchema<T>): boolean => {
      const result = schema.safeParse(values);
      if (result.success) {
        setErrors({});
        return true;
      }
      const fieldErrors: Errors<T> = {};
      result.error.errors.forEach((e) => {
        const key = e.path[0] as keyof T;
        if (key) fieldErrors[key] = e.message;
      });
      setErrors(fieldErrors);
      return false;
    },
    [values]
  );

  const setValue = useCallback((name: keyof T, value: unknown) => {
    setValues((v) => ({ ...v, [name]: value }));
  }, []);

  const reset = useCallback(() => {
    setValues(initial);
    setErrors({});
  }, [initial]);

  return { values, errors, handleChange, validate, setValue, reset };
}
