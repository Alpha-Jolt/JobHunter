import { ResumeUpload } from "@/features/resume/ResumeUpload";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";

export default function ResumePage() {
  return (
    <div className="flex flex-col gap-6 max-w-2xl">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Resume</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Upload your master resume. AI will tailor it per job — no fabrication, ever.
        </p>
      </div>
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
