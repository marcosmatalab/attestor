"use client";

import { useLocale } from "@/lib/i18n/LocaleProvider";
import styles from "./chrome.module.css";

const LOCALES = [
  { code: "en", label: "EN" },
  { code: "es", label: "ES" },
] as const;

export function LanguageToggle() {
  const { locale, setLocale, t } = useLocale();
  return (
    <div className={styles.langToggle} role="group" aria-label={t("header.languageLabel")}>
      {LOCALES.map(({ code, label }) => (
        <button
          key={code}
          type="button"
          className={`${styles.langButton} ${locale === code ? styles.langButtonActive : ""}`}
          aria-pressed={locale === code}
          onClick={() => setLocale(code)}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
