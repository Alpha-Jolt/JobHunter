import { ApplicationHistory } from "@/features/applications/ApplicationHistory";
import { PageHeader } from "@/shared/components/Motion";

export default function ApplicationsPage() {
  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <PageHeader
        label="Outbox"
        title="Applications"
        description="Track every send — status, timestamps, and follow-ups in one place."
      />
      <ApplicationHistory />
    </div>
  );
}
