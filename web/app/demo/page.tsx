"use client";

import { useState } from "react";
import { api, type DemoResult } from "@/lib/api";
import { LedgerCard } from "@/components/LedgerCard";
import { ProvenanceCard } from "@/components/ProvenanceCard";
import { Badge, Button, Callout, Card, KeyValue, KV, Mono, Skeleton, type Tone } from "@/components/ui";
import sx from "@/components/sections.module.css";

const RISK_TONE: Record<string, Tone> = {
  prohibited: "prohibited",
  high: "high",
  limited: "limited",
  minimal: "minimal",
};

export default function DemoPage() {
  const [result, setResult] = useState<DemoResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      setResult(await api.demo());
    } catch (err) {
      setError(err instanceof Error ? err.message : "The request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <h1 className={sx.title}>End-to-end demo</h1>
      <p className={sx.lead}>
        One example path for a high-risk <strong>provider</strong>: classify → Annex IV → sign an AI
        output (C2PA) → verify → anchor in the ledger → verify the ledger offline. Every output is
        produced live by the engine; signing and sealing use ephemeral dev keys generated per run.
      </p>

      <Card>
        <Button onClick={run} busy={loading}>
          {loading ? "Running the pipeline…" : "Run the demo"}
        </Button>
      </Card>

      <div className={sx.results} aria-live="polite" aria-busy={loading}>
        {error && (
          <Callout tone="error" role="alert">
            {error}
          </Callout>
        )}
        {loading && (
          <Card title="Running the pipeline…">
            <Skeleton lines={4} />
          </Card>
        )}
        {!loading && result && (
          <>
            <Card title="Classification">
              <div className={sx.badgeRow}>
                <Badge tone={RISK_TONE[result.classification.risk] ?? "neutral"}>
                  {result.classification.risk}
                </Badge>
              </div>
              <KeyValue>
                <KV k="Checksum">
                  <Mono>{result.classification.checksum}</Mono>
                </KV>
                <KV k="Annex IV">
                  {result.annex_iv.system_name} — {result.annex_iv.sections.length} sections
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
