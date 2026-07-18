import * as React from "react";
import { cn } from "@/shared/utils/cn";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, label, error, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-foreground">
            {label}
          </label>
        )}
        <input
          id={inputId}
          ref={ref}
          className={cn(
            "h-11 w-full rounded-[var(--radius-sm)] border border-input-border bg-input px-3.5 text-[15px] text-foreground placeholder:text-muted-foreground",
            "transition-[border-color,box-shadow] duration-200",
            "focus:outline-none focus:border-primary focus:shadow-[0_0_0_3px_var(--ember-glow)]",
            "disabled:opacity-50 disabled:cursor-not-allowed",
            error && "border-destructive focus:shadow-[0_0_0_3px_var(--ember-glow)]",
            className
          )}
          {...props}
        />
        {error && <p className="text-xs font-medium text-destructive">{error}</p>}
      </div>
    );
  }
);
Input.displayName = "Input";
