/** The three verdict cards. Every value shown comes from the engine response.
 *
 * The provenance card deliberately shows the validation state and the signer's
 * trust as two separate lines: collapsing them into one tick is the exact
 * mistake the C2PA verifier was written to avoid.
 */

import { Badge, riskTone } from "@/components/Badge";
import { getDictionary } from "@/lib/i18n/dictionaries";
import type { DemoResult } from "@/lib/types";

function Row({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div className="row">
      <dt>{label}</dt>
      <dd className={mono ? "mono" : undefined}>{value}</dd>
    </div>
  );
}

export function DemoResultCards({ result, locale }: { result: DemoResult; locale?: string }) {
  const t = getDictionary(locale);
  const { classification, provenance, ledger, annex_iv: annexIv } = result;

  return (
    <section className="grid">
      <article className="card">
        <h2>
          {t.cards.classification}
          <Badge tone={riskTone(classification.risk)}>{classification.risk}</Badge>
        </h2>
        <dl style={{ margin: 0 }}>
          <Row label={t.cards.checksum} value={classification.checksum} mono />
          <Row label={t.cards.bundle} value={result.bundle.version} />
          <Row label={t.cards.obligations} value={String(classification.obligations.length)} />
        </dl>
      </article>

      <article className="card">
        <h2>
          {t.cards.annexIv}
          <Badge tone="ok">{annexIv.citation_count} ✓</Badge>
        </h2>
        <dl style={{ margin: 0 }}>
          <Row label={t.cards.sections} value={String(annexIv.section_count)} />
          <Row label={t.cards.citations} value={String(annexIv.citation_count)} />
          <Row label="sha256" value={annexIv.dossier_sha256} mono />
        </dl>
      </article>

      <article className="card">
        <h2>
          {t.cards.provenance}
          <Badge tone={provenance.trusted ? "ok" : "warn"}>
            {provenance.trusted ? t.status.trusted : t.status.untrusted}
          </Badge>
        </h2>
        <dl style={{ margin: 0 }}>
          <Row label={t.cards.validationState} value={provenance.validation_state} />
          <Row label={t.cards.signer} value={provenance.signer ?? "—"} />
        </dl>
        <p style={{ fontSize: "0.82rem", color: "var(--muted)", marginBottom: 0 }}>
          {provenance.headline}
        </p>
      </article>

      <article className="card">
        <h2>
          {t.cards.ledger}
          <Badge tone={ledger.verification.verified ? "ok" : "bad"}>
            {ledger.verification.verified ? t.status.verified : t.status.tampered}
          </Badge>
        </h2>
        <dl style={{ margin: 0 }}>
          <Row label={t.cards.merkleRoot} value={ledger.signed_root.merkle_root} mono />
          <Row label={t.cards.records} value={String(ledger.leaf_count)} />
          <Row label={t.cards.integrity} value={String(ledger.verification.integrity_ok)} />
          <Row label={t.cards.signature} value={String(ledger.verification.signature_ok)} />
        </dl>
      </article>
    </section>
  );
}
