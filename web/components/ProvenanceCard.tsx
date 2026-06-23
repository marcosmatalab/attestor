import type { Provenance } from "@/lib/api";
import { Badge, Callout, Card, KeyValue, KV, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function ProvenanceCard({ prov }: { prov: Provenance }) {
  return (
    <Card title="C2PA provenance">
      <div className={sx.badgeRow}>
        {/* Untrusted is reported in amber — correctly untrusted, not an error/tamper. */}
        <Badge tone={prov.trusted ? "ok" : "warn"}>
          {prov.trusted ? "signer trusted" : "signer untrusted"}
        </Badge>
      </div>
      <p className={sx.headline}>{prov.headline}</p>
      <Callout tone="caveat">
        Integrity (<strong>{prov.validation_state}</strong>) means the manifest is intact — it
        does{" "}
        <strong>not</strong> mean the signer is trusted. The demo&apos;s dev certificate is on no
        C2PA trust list, so the signer is reported <strong>untrusted</strong>. &quot;Valid&quot; is
        never shown without the trust qualifier.
      </Callout>
      {prov.signer && (
        <KeyValue>
          <KV k="Signer">
            <Mono>{prov.signer.common_name}</Mono> · {prov.signer.algorithm}
          </KV>
          {prov.ai_disclosure && (
            <KV k="AI disclosure">
              <Mono>{prov.ai_disclosure.digital_source_type ?? "—"}</Mono>
            </KV>
          )}
        </KeyValue>
      )}
    </Card>
  );
}
