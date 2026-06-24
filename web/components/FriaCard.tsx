"use client";

import type { Fria } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Callout, Card, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function FriaCard({ fria, note }: { fria: Fria | null; note: string | null }) {
  const { t } = useLocale();
  if (!fria) {
    return (
      <Card title={t("fria.titleNotApplicable")}>
        <Callout tone="muted">{note ?? t("fria.notApplicable")}</Callout>
      </Card>
    );
  }
  return (
    <Card title={t("fria.titleApplicable")}>
      {/* trigger / reference / date are engine output, interpolated verbatim. */}
      <p className={sx.meta}>
        {t("fria.meta", {
          trigger: fria.trigger,
          reference: fria.fria_reference,
          date: fria.fria_effective_date,
        })}
      </p>
      <Callout tone="caveat">{fria.disclaimer}</Callout>
      <ul className={sx.citeList}>
        {fria.sections.map((s) => (
          <li key={s.point}>
            <strong>({s.point})</strong> {s.requirement}
            <div className={sx.meta}>
              <Mono>{s.placeholder}</Mono>
            </div>
          </li>
        ))}
      </ul>
      <p className={sx.fineprint}>{fria.notify_authority_note}</p>
    </Card>
  );
}
