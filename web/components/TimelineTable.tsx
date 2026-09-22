"use client";

import type { Timeline } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Callout, Card, Mono, TableWrap, cellDiverges } from "@/components/ui";

export function TimelineTable({ timeline }: { timeline: Timeline }) {
  const { t } = useLocale();
  // The status is engine output, read from the binding bundle's meta — interpolated
  // verbatim. The fallback is only for an empty response, never a second source of truth.
  const status = timeline.omnibus_status || "in force";
  return (
    <Card title={t("timeline.title")}>
      <Callout tone="caveat">{t("timeline.caveat", { status })}</Callout>
      <TableWrap>
        <thead>
          <tr>
            <th scope="col">{t("timeline.thObligation")}</th>
            <th scope="col">{t("timeline.thLegalText")}</th>
            <th scope="col">{t("timeline.thOmnibus")}</th>
          </tr>
        </thead>
        <tbody>
          {timeline.obligations.map((o) => {
            const diverges = o.legal_text_date !== o.omnibus_date;
            return (
              <tr key={o.id}>
                <td>
                  <Mono>{o.reference}</Mono> {o.title}
                </td>
                <td>{o.legal_text_date ?? "—"}</td>
                <td className={diverges ? cellDiverges : undefined}>{o.omnibus_date ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </TableWrap>
    </Card>
  );
}
