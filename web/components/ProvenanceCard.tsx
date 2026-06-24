"use client";

import type { Provenance } from "@/lib/api";
import { useLocale } from "@/lib/i18n/LocaleProvider";
import { Badge, Callout, Card, KeyValue, KV, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function ProvenanceCard({ prov }: { prov: Provenance }) {
  const { t } = useLocale();
  return (
    <Card title={t("provenance.title")}>
      <div className={sx.badgeRow}>
        {/* Verdict token: engine output, kept verbatim (never translated) in every locale. */}
        <Badge tone={prov.trusted ? "ok" : "warn"}>
          {prov.trusted ? "signer trusted" : "signer untrusted"}
        </Badge>
      </div>
      <p className={sx.headline}>{prov.headline}</p>
      <Callout tone="caveat">{t("provenance.caveat", { state: prov.validation_state ?? "" })}</Callout>
      {prov.signer && (
        <KeyValue>
          <KV k={t("provenance.signer")}>
            <Mono>{prov.signer.common_name}</Mono> · {prov.signer.algorithm}
          </KV>
          {prov.ai_disclosure && (
            <KV k={t("provenance.aiDisclosure")}>
              <Mono>{prov.ai_disclosure.digital_source_type ?? "—"}</Mono>
            </KV>
          )}
        </KeyValue>
      )}
    </Card>
  );
}
