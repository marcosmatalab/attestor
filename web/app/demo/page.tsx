"use client";

import { useState } from "react";
import { api, type DemoResult } from "@/lib/api";
import { LedgerCard } from "@/components/LedgerCard";
import { ProvenanceCard } from "@/components/ProvenanceCard";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Badge, Button, Callout, Card, KeyValue, KV, Mono, Skeleton, type Tone } from "@/components/ui";
import sx from "@/components/sections.module.css";

const RISK_TONE: Record<string, Tone> = {
  prohibited: "prohibited",
  high: "high",
  limited: "limited",
  minimal: "minimal",
};

export default function DemoPage() {
  const { t } = useLocale();
  const [result, setResult] = useState<DemoResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.demo());
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.requestFailed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className={sx.title}>{t("demo.title")}</h1>
      <p className={sx.lead}>{t("demo.lead")}</p>

      <Card>
        <Button onClick={run} busy={loading}>
          {loading ? t("demo.running") : t("demo.run")}
        </Button>
      </Card>

      <div className={sx.results} aria-live="polite" aria-busy={loading}>
        {error && (
          <Callout tone="error" role="alert">
            {error}
          </Callout>
        )}
        {loading && (
          <Card title={t("demo.running")}>
            <Skeleton lines={4} />
          </Card>
        )}
        {!loading && result && (
          <>
            <Card title={t("demo.classification")}>
              <div className={sx.badgeRow}>
                {/* Risk enum is engine output — verbatim. */}
                <Badge tone={RISK_TONE[result.classification.risk] ?? "neutral"}>
                  {result.classification.risk}
                </Badge>
              </div>
              <KeyValue>
                <KV k={t("demo.checksum")}>
                  <Mono>{result.classification.checksum}</Mono>
                </KV>
                <KV k={t("demo.annexiv")}>
                  {t("demo.annexivSummary", {
                    name: result.annex_iv.system_name,
                    n: result.annex_iv.sections.length,
                  })}
                </KV>
              </KeyValue>
            </Card>
            <ProvenanceCard prov={result.provenance} />
            <LedgerCard
              ledger={result.ledger.verification}
              merkleRoot={result.ledger.signed_root.merkle_root}
              records={result.ledger.records.length}
            />
          </>
        )}
      </div>
    </>
  );
}
