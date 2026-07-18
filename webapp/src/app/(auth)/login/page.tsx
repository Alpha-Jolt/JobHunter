import Link from "next/link";
import { LoginForm } from "@/features/auth/LoginForm";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/components/Card";

export default function LoginPage() {
  return (
    <Card className="shadow-[0_24px_48px_-24px_rgba(16,16,18,0.18)]">
      <CardHeader className="pb-2">
        <p className="section-label !mb-2">Welcome back</p>
        <CardTitle className="text-xl">Sign in to your account</CardTitle>
      </CardHeader>
      <CardContent>
        <LoginForm />
        <p className="mt-5 text-center text-sm text-muted-foreground">
          Don&apos;t have an account?{" "}
          <Link href="/signup" className="text-foreground font-semibold hover:text-ember transition-colors">
            Sign up
          </Link>
        </p>
      </CardContent>
    </Card>
  );
}
