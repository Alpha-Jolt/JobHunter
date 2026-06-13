"use client";

import { useState, useCallback } from "react";
import { ApiError } from "@/shared/api/errors";

interface AsyncState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

interface UseAsyncReturn<T, A extends unknown[]> extends AsyncState<T> {
  execute: (...args: A) => Promise<T | null>;
  reset: () => void;
}

export function useAsync<T, A extends unknown[]>(
  fn: (...args: A) => Promise<T>
): UseAsyncReturn<T, A> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    isLoading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: A): Promise<T | null> => {
      setState({ data: null, isLoading: true, error: null });
      try {
        const data = await fn(...args);
        setState({ data, isLoading: false, error: null });
        return data;
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : "An unexpected error occurred.";
        setState({ data: null, isLoading: false, error: message });
        return null;
      }
    },
    [fn]
  );

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, error: null });
  }, []);

  return { ...state, execute, reset };
}
