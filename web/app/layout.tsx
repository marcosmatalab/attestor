import type { Metadata } from "next";
import Link from "next/link";
import { getDictionary } from "@/lib/i18n/dictionaries";
import "./globals.css";

export const metadata: Metadata = {
  title: "Attestor — deterministic EU AI Act compliance engine",
  description:
    "Deterministic EU AI Act classification with an offline-verifiable cryptographic ledger.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const t = getDictionary("en");
  return (
    <html lang="en">
      <body>
        <div className="shell">
          <header className="topbar">
            <strong>Attestor</strong>
            <nav>
              <Link href="/">{t.nav.home}</Link>
              <Link href="/demo">{t.nav.demo}</Link>
            </nav>
          </header>
          {children}
          <footer>
            Not legal advice. Compliance support and evidence, designed for human review.
          </footer>
        </div>
      </body>
    </html>
  );
}
