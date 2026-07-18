import Link from "next/link";
import { SignupForm } from "@/features/auth/SignupForm";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";

export default function SignupPage() {
  return (
    <Card className="shadow-[0_24px_48px_-24px_rgba(16,16,18,0.18)]">
      <CardHeader className="pb-2">
        <p className="section-label !mb-2">Get started</p>
        <CardTitle className="text-xl">Create your account</CardTitle>
      </CardHeader>
      <CardContent>
        <SignupForm />
        <p className="mt-5 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link href="/login" className="text-foreground font-semibold hover:text-ember transition-colors">
            Sign in
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
