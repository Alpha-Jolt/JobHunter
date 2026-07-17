import { NextResponse, type NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/signup"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Allow public paths and Next.js internals
  if (
    PUBLIC_PATHS.some((p) => pathname.startsWith(p)) ||
    pathname.startsWith("/u/") ||
    pathname.startsWith("/_next") ||
    pathname.startsWith("/api") ||
    pathname === "/manifest.json" ||
    pathname.startsWith("/icons")
  ) {
    return NextResponse.next();
  }

  // Access token is in memory (Zustand). Refresh cookie is set by the API on
  // api.myjobhunter.in (optionally Domain=.myjobhunter.in). Middleware on the
  // app host cannot reliably gate on that cookie across subdomains — AuthGuard
  // handles silent refresh + redirect on the client.
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.png|icons|manifest.json).*)"],
};
