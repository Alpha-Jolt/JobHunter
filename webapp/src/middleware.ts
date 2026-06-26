import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths and Next.js internals
  if (
    PUBLIC_PATHS.some((p) => pathname.startsWith(p)) ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname === "/manifest.json" ||
    pathname.startsWith("/icons")
  ) {
    return NextResponse.next();
  }

  // The access token lives in memory (Zustand), not in cookies.
  // We cannot inspect it in middleware. Instead, the client-side AuthGuard
  // handles redirects. Middleware only blocks if there is no refresh cookie,
  // which signals a definitely-unauthenticated session.
  const refreshCookie = request.cookies.get("refresh_token");
  if (!refreshCookie) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|icons|manifest.json).*)"],
};
