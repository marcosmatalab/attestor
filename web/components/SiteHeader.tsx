"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { LanguageToggle } from "./LanguageToggle";
import styles from "./chrome.module.css";

export function SiteHeader() {
  const pathname = usePathname();
  const { t } = useLocale();
  const links = [
    { href: "/", label: t("header.navClassify") },
    { href: "/demo", label: t("header.navDemo") },
  ];
  return (
    <header className={styles.header}>
      <div className={`container ${styles.headerInner}`}>
        <p className={styles.brand}>
          Attestor <span className={styles.tagline}>{t("header.tagline")}</span>
        </p>
        <div className={styles.headerRight}>
          <nav aria-label="Primary">
            <ul className={styles.nav} style={{ listStyle: "none", margin: 0, padding: 0 }}>
              {links.map((link) => {
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
          <LanguageToggle />
        </div>
      </div>
    </header>
  );
}
