"use client";

import type { LedgerVerification } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Badge, Callout, Card, KeyValue, KV, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function LedgerCard({
  ledger,
  merkleRoot,
  records,
}: {
  ledger: LedgerVerification;
  merkleRoot: string;
  records: number;
}) {
  const { t } = useLocale();
  return (
    <Card title={t("ledger.title")}>
      <div className={sx.badgeRow}>
        {/* Verdict token: engine output, verbatim. */}
        <Badge tone={ledger.verified ? "ok" : "warn"}>
          {ledger.verified ? "verified" : "tampered"}
        </Badge>
      </div>
      <p className={sx.headline}>{ledger.headline}</p>
      <KeyValue>
        <KV k={t("ledger.merkleRoot")}>
          <Mono>{merkleRoot}</Mono>
        </KV>
        <KV k={t("ledger.anchoredRecords")}>{records}</KV>
      </KeyValue>
      <Callout tone="note">{t("ledger.caveat")}</Callout>
    </Card>
  );
}
