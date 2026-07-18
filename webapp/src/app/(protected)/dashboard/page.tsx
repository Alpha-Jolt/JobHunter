import Link from "next/link";
import { Briefcase, FileText, Layers, ArrowUpRight } from "lucide-react";
import { DashboardMetricsGrid } from "@/features/dashboard/DashboardMetrics";
import { Button } from "@/shared/components/Button";
import { Card, CardContent } from "@/shared/components/Card";
import { PageHeader, FadeUp, Stagger, StaggerItem } from "@/shared/components/Motion";

const shortcuts = [
  {
    href: "/jobs",
    title: "Browse Jobs",
    desc: "Scan the queue and pick roles worth your time.",
    icon: Briefcase,
  },
  {
    href: "/resume",
    title: "Manage Resume",
    desc: "Keep a master resume ready for every tailor pass.",
    icon: FileText,
  },
  {
    href: "/variants",
    title: "Review Variants",
    desc: "Approve tailored drafts before they go out.",
    icon: Layers,
  },
];

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-8">
      <PageHeader
        label="Overview"
        title="Your hunt, at a glance"
        description="Track open roles, pending variants, and applications — then move the next one forward."
      />

      <FadeUp delay={0.08}>
        <DashboardMetricsGrid />
      </FadeUp>

      <Stagger className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {shortcuts.map(({ href, title, desc, icon: Icon }) => (
          <StaggerItem key={href}>
            <Link href={href} className="block h-full group">
              <Card className="h-full hover:border-border-strong">
                <CardContent className="pt-6 flex flex-col gap-4">
                  <div className="flex items-start justify-between">
                    <div className="h-11 w-11 rounded-[var(--radius-sm)] bg-accent text-accent-foreground flex items-center justify-center">
                      <Icon className="h-5 w-5" />
                    </div>
                    <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 -translate-y-1 translate-x-1 group-hover:opacity-100 group-hover:translate-x-0 group-hover:translate-y-0 transition-all duration-300" />
                  </div>
                  <div>
                    <h3 className="font-display text-lg font-medium text-foreground">{title}</h3>
                    <p className="mt-1 text-sm text-foreground-muted leading-relaxed">{desc}</p>
                  </div>
                  <Button variant="ghost" className="w-fit px-0 h-auto min-h-0 text-ember hover:bg-transparent hover:text-ember">
                    Open →
                  </Button>
                </CardContent>
              </Card>
            </Link>
          </StaggerItem>
        ))}
      </Stagger>
    </div>
  );
}
