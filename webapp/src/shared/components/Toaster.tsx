"use client";

import * as React from "react";
import * as ToastPrimitive from "@radix-ui/react-toast";
import { X } from "lucide-react";
import { cn } from "@/shared/utils/cn";
import { useUiStore } from "@/shared/state/uiStore";

const variantStyles = {
  success: "bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300",
  error: "bg-red-50 border-red-200 text-red-800 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300",
  warning: "bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300",
  info: "bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/20 dark:border-blue-800 dark:text-blue-300",
};

export function Toaster() {
  const { toasts, removeToast } = useUiStore();

  return (
    <ToastPrimitive.Provider>
      {toasts.map((t) => (
        <ToastPrimitive.Root
          key={t.id}
          open
          onOpenChange={(open) => !open && removeToast(t.id)}
          className={cn(
            "flex items-start gap-3 rounded-lg border p-4 shadow-lg w-80 text-sm",
            variantStyles[t.type]
          )}
        >
          <ToastPrimitive.Description className="flex-1">{t.message}</ToastPrimitive.Description>
          <ToastPrimitive.Close asChild>
            <button className="shrink-0 opacity-60 hover:opacity-100">
              <X className="h-4 w-4" />
            </button>
          </ToastPrimitive.Close>
        </ToastPrimitive.Root>
      ))}
      <ToastPrimitive.Viewport className="fixed bottom-4 right-4 z-50 flex flex-col gap-2" />
    </ToastPrimitive.Provider>
  );
}
