import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/utils/cn";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap font-semibold tracking-[-0.01em] transition-[transform,filter,background,color,border-color] duration-250 ease-[cubic-bezier(0.16,1,0.3,1)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 active:scale-[0.99]",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground hover:brightness-[0.94] hover:-translate-y-px min-h-[44px] px-5 rounded-[var(--radius-sm)]",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80 min-h-[44px] px-5 rounded-[var(--radius-sm)]",
        destructive:
          "bg-destructive text-destructive-foreground hover:brightness-[0.94] min-h-[44px] px-5 rounded-[var(--radius-sm)]",
        outline:
          "border border-border-strong bg-transparent text-foreground hover:border-foreground hover:-translate-y-px min-h-[44px] px-5 rounded-[var(--radius-sm)]",
        ghost:
          "text-foreground hover:bg-secondary min-h-[44px] px-4 rounded-[var(--radius-sm)]",
        link: "text-primary underline-offset-4 hover:underline px-0 font-medium",
        ink: "bg-ink text-paper hover:brightness-125 hover:-translate-y-px min-h-[44px] px-5 rounded-[var(--radius-sm)] dark:bg-paper dark:text-ink",
      },
      size: {
        sm: "h-9 px-3.5 text-xs rounded-[var(--radius-sm)]",
        md: "min-h-[44px] px-5 text-[15px]",
        lg: "min-h-[52px] px-6 text-base",
        icon: "h-11 w-11 rounded-[var(--radius-sm)]",
      },
    },
    defaultVariants: { variant: "default", size: "md" },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild, isLoading, children, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(buttonVariants({ variant, size }), className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            <span>Loading…</span>
          </>
        ) : (
          children
        )}
      </Comp>
    );
  }
);
Button.displayName = "Button";
