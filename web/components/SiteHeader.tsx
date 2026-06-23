"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import styles from "./chrome.module.css";

const LINKS = [
  { href: "/", label: "Classify" },
  { href: "/demo", label: "End-to-end demo" },
];

export function SiteHeader() {
  const pathname = usePathname();
  return (
    <header className={styles.header}>
      <div className={`container ${styles.headerInner}`}>
        <p className={styles.brand}>
          Attestor <span className={styles.tagline}>deterministic EU AI Act engine</span>
        </p>
        <nav aria-label="Primary">
          <ul className={styles.nav} style={{ listStyle: "none", margin: 0, padding: 0 }}>
            {LINKS.map((link) => {
              const active = pathname === link.href;
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={`${styles.navLink} ${active ? styles.navLinkActive : ""}`}
                    aria-current={active ? "page" : undefined}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </div>
    </header>
  );
}
