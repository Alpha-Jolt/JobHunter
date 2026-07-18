import type { Metadata, Viewport } from "next";
import { Fraunces, Inter, IBM_Plex_Mono, Fredoka } from "next/font/google";
import { ThemeProvider } from "next-themes";
import { Toaster } from "@/shared/components/Toaster";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  display: "swap",
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-ibm-plex-mono",
  display: "swap",
});

const fredoka = Fredoka({
  subsets: ["latin"],
  weight: ["500", "600"],
  variable: "--font-fredoka",
  display: "swap",
});

export const metadata: Metadata = {
  title: "JobHunter",
  description: "AI-powered job application automation",
  manifest: "/manifest.json",
};

export const viewport: Viewport = {
  themeColor: "#ff8f34",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${fraunces.variable} ${ibmPlexMono.variable} ${fredoka.variable}`}
    >
      <body className="font-sans antialiased">
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          {children}
          <Toaster />
        </ThemeProvider>
      </body>
    </html>
  );
}
