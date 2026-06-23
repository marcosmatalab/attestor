import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { HonestyBanner } from "@/components/HonestyBanner";
import { SiteHeader } from "@/components/SiteHeader";

// Self-hosted (vendored) variable fonts — no network at build time, so the build is offline
// and self-contained, consistent with the rest of the project. Licenses live in app/fonts/.
const inter = localFont({
  src: "./fonts/inter-variable.woff2",
  variable: "--font-inter",
  weight: "100 900",
  display: "swap",
});
const jetbrainsMono = localFont({
  src: "./fonts/jetbrains-mono-variable.woff2",
  variable: "--font-jbmono",
  weight: "100 800",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Attestor — EU AI Act compliance engine (portfolio demo)",
  description:
    "Deterministic EU AI Act risk classification, Annex IV dossier, C2PA provenance, and an offline-verifiable ledger. Portfolio demonstration — not legal advice.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <body>
        <SiteHeader />
        <HonestyBanner />
        <main>
          <div className="container">{children}</div>
        </main>
      </body>
    </html>
  );
}
