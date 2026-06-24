"use client";

import type { Crosswalk } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Callout, Card, Mono, TableWrap } from "@/components/ui";

export function CrosswalkCard({ crosswalk }: { crosswalk: Crosswalk }) {
  const { t } = useLocale();
  return (
    <Card title={t("crosswalk.title")}>
      {/* The disclaimer, obligation refs/titles and ISO ids are engine output — verbatim. */}
      <Callout tone="note">{crosswalk.disclaimer}</Callout>
      <TableWrap>
        <thead>
          <tr>
            <th scope="col">{t("crosswalk.thObligation")}</th>
            <th scope="col">{t("crosswalk.thIso")}</th>
          </tr>
        </thead>
        <tbody>
          {crosswalk.entries.map((e) => (
            <tr key={e.obligation_id}>
              <td>
                <Mono>{e.reference}</Mono> {e.title}
              </td>
              <td>{e.iso_references.map((ref) => ref.label).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </TableWrap>
    </Card>
  );
}
