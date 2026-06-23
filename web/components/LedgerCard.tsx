import type { LedgerVerification } from "@/lib/api";
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
  return (
    <Card title="Ledger (offline verification)">
      <div className={sx.badgeRow}>
        <Badge tone={ledger.verified ? "ok" : "warn"}>
          {ledger.verified ? "verified" : "tampered"}
        </Badge>
      </div>
      <p className={sx.headline}>{ledger.headline}</p>
      <KeyValue>
        <KV k="Merkle root">
          <Mono>{merkleRoot}</Mono>
        </KV>
        <KV k="Anchored records">{records}</KV>
      </KeyValue>
      <Callout tone="note">
        An append-only log with cryptographic integrity, verifiable offline by a third party —{" "}
        <strong>not a blockchain</strong> (no distribution, no consensus). The integrity and
        signature decide the verdict; TSA trust, when present, is reported separately.
      </Callout>
    </Card>
  );
}
