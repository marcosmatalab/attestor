"use client";

import type { Dossier } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Callout, Card, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function AnnexIvCard({ dossier, note }: { dossier: Dossier | null; note: string | null }) {
  const { t } = useLocale();
  if (!dossier) {
    return (
      <Card title={t("annexiv.title")}>
        {/* `note` is the engine's own gated message — rendered verbatim. */}
        <Callout tone="muted">{note ?? t("annexiv.notApplicable")}</Callout>
      </Card>
    );
  }
  return (
    <Card title={t("annexiv.title")}>
      <Callout tone="note">{t("annexiv.validatedNote")}</Callout>
      {dossier.sections.map((s) => (
        <div key={s.number} className={sx.sectionItem}>
          <strong>
            {s.number}. {s.title}
          </strong>
          {s.citations.length > 0 ? (
            <ul className={sx.citeList}>
              {s.citations.map((cit) => (
                <li key={cit.obligation_id}>
                  <Mono>{cit.reference}</Mono> {cit.title} ({cit.effective_date})
                </li>
              ))}
            </ul>
          ) : (
            <div className={sx.meta}>{t("annexiv.noCitations")}</div>
          )}
        </div>
      ))}
    </Card>
  );
}
