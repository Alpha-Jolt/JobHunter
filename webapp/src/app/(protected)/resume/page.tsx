import { ResumeUpload } from "@/features/resume/ResumeUpload";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";
import { PageHeader } from "@/shared/components/Motion";

export default function ResumePage() {
  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <PageHeader
        label="Master file"
        title="Resume"
        description="Upload your master resume. AI will tailor it per job — no fabrication, ever."
      />
      <Card>
        <CardHeader>
          <CardTitle>Master Resume</CardTitle>
        </CardHeader>
        <CardContent>
          <ResumeUpload />
        </CardContent>
      </Card>
    </div>
  );
}
