"use client";

import type { Classification } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Badge, Card, KeyValue, KV, Mono, TableWrap, type Tone } from "@/components/ui";
import sx from "./sections.module.css";

const RISK_TONE: Record<string, Tone> = {
  prohibited: "prohibited",
  high: "high",
  limited: "limited",
  minimal: "minimal",
};

export function ClassificationCard({ c }: { c: Classification }) {
  const { t } = useLocale();
  return (
    <Card title={t("classification.title")}>
      <div className={sx.badgeRow}>
        {/* Risk enum is engine output — rendered verbatim, never translated. */}
        <Badge tone={RISK_TONE[c.risk] ?? "neutral"}>{c.risk}</Badge>
      </div>
      <KeyValue>
        <KV k={t("classification.bundle")}>
          {c.bundle_version} <Mono>({c.bundle_sha256.slice(0, 16)}…)</Mono>
        </KV>
        <KV k={t("classification.checksum")}>
          <Mono>{c.checksum}</Mono>
        </KV>
      </KeyValue>
      <TableWrap caption={t("classification.caption")}>
        <thead>
          <tr>
            <th scope="col">{t("classification.thObligation")}</th>
            <th scope="col">{t("classification.thReference")}</th>
            <th scope="col">{t("classification.thEffective")}</th>
          </tr>
        </thead>
        <tbody>
          {c.obligations.map((o) => (
            <tr key={o.id}>
              <td>{o.title}</td>
              <td>
                <Mono>{o.reference}</Mono>
              </td>
              <td>{o.effective_date}</td>
            </tr>
          ))}
        </tbody>
      </TableWrap>
    </Card>
  );
}
