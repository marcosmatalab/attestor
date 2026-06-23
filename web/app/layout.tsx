import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Attestor — EU AI Act compliance engine (portfolio demo)",
  description:
    "Deterministic EU AI Act risk classification, Annex IV dossier, C2PA provenance, and an offline-verifiable ledger. Portfolio demonstration — not legal advice.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${geistSans.variable} ${geistMono.variable}`}>
      <body>
        <header className="site-header">
          <div className="container">
            <h1>
              Attestor <span className="tagline">deterministic EU AI Act engine</span>
            </h1>
            <nav>
              <Link href="/">Classify</Link>
              <Link href="/demo">End-to-end demo</Link>
            </nav>
          </div>
        </header>
        <div className="honesty">
          <div className="container">
            <strong>Portfolio demonstration — not legal advice, not a compliance product.</strong>{" "}
            Every figure, date, checksum, and verdict below comes from a deterministic engine; the
            UI only displays it. No system is &quot;compliant&quot; or &quot;certified&quot; by this tool.
          </div>
        </div>
        <main>
          <div className="container">{children}</div>
        </main>
      </body>
    </html>
  );
}
