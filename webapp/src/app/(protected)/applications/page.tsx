import { ApplicationHistory } from "@/features/applications/ApplicationHistory";

export default function ApplicationsPage() {
  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Applications</h1>
        <p className="text-sm text-muted-foreground mt-1">Track your sent applications.</p>
      </div>
      <ApplicationHistory />
    </div>
  );
}
