import type { NextConfig } from "next";

const minioUrl = process.env.NEXT_PUBLIC_MINIO_URL ?? "http://localhost:9000";
const parsedMinioUrl = new URL(minioUrl);
const rawApiUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const apiUrl =
  rawApiUrl === "" || rawApiUrl === "/" || rawApiUrl === "same-origin"
    ? ""
    : rawApiUrl.replace(/\/$/, "");
const internalApiUrl = process.env.INTERNAL_API_URL ?? "http://localhost:8000";

const connectSrc = [
  "'self'",
  apiUrl,
  minioUrl,
  "https://cloudflareinsights.com",
  "https://*.cloudflareinsights.com",
]
  .filter(Boolean)
  .join(" ");

const nextConfig: NextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      {
        protocol: parsedMinioUrl.protocol.replace(":", "") as "http" | "https",
        hostname: parsedMinioUrl.hostname,
        port: parsedMinioUrl.port,
      },
    ],
  },

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${internalApiUrl}/api/:path*`,
      },
      // Health proxied for same-origin checks
      {
        source: "/health",
        destination: `${internalApiUrl}/health`,
      },
    ];
  },

  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'self'",
              // Cloudflare Web Analytics beacon (injected by CF when enabled)
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://static.cloudflareinsights.com",
              "style-src 'self' 'unsafe-inline'",
              `img-src 'self' data: blob: ${minioUrl}`,
              "font-src 'self'",
              `connect-src ${connectSrc}`,
            ].join("; "),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
