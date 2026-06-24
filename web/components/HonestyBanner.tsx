"use client";

import { useLocale } from "@/lib/i18n/LocaleProvider";
import styles from "./chrome.module.css";

/** A persistent, prominent honesty notice. Never hidden by the redesign or i18n. */
export function HonestyBanner() {
  const { t } = useLocale();
  return (
    <div className={styles.banner} role="note">
      <div className="container">
        <strong>{t("honesty.bannerLead")}</strong> {t("honesty.bannerRest")}
      </div>
    </div>
  );
}
