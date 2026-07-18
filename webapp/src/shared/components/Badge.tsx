import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/shared/utils/cn";

const badgeVariants = cva(
  "inline-flex items-center font-mono text-[11px] font-medium tracking-[0.06em] uppercase rounded-md px-2 py-0.5 border",
  {
    variants: {
      variant: {
        default: "bg-accent text-accent-foreground border-transparent",
        secondary: "bg-[var(--fill-faint)] text-foreground border-border",
        success: "bg-[var(--fill-faint)] text-foreground border-border",
        warning: "bg-accent text-accent-foreground border-transparent",
        destructive: "bg-accent text-accent-foreground border-transparent",
        outline: "bg-transparent text-muted-foreground border-border",
      },
    },
    defaultVariants: { variant: "default" },
  }
);

interface BadgeProps extends VariantProps<typeof badgeVariants> {
  className?: string;
  children: React.ReactNode;
}

export function Badge({ className, variant, children }: BadgeProps) {
  return <span className={cn(badgeVariants({ variant }), className)}>{children}</span>;
}
