import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  async rewrites() {
    // Server-side proxy target (Docker service name in compose, or localhost in dev)
    const apiUrl = process.env.ADMIN_API_INTERNAL_URL
      ?? process.env.NEXT_PUBLIC_ADMIN_API_URL
      ?? "http://localhost:8003";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
    ];
  },
  async headers() {
    const connectSrc = [
      "'self'",
      process.env.NEXT_PUBLIC_ADMIN_API_URL,
      process.env.ADMIN_API_INTERNAL_URL,
      "http://localhost:8003",
      "https://admin-api.myjobhunter.in",
    ]
      .filter(Boolean)
      .join(" ");

    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://static.cloudflareinsights.com",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data: blob:",
              "font-src 'self'",
              `connect-src ${connectSrc} https://cloudflareinsights.com https://*.cloudflareinsights.com`,
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
