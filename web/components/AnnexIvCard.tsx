import type { Dossier } from "@/lib/api";
import { Callout, Card, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function AnnexIvCard({ dossier, note }: { dossier: Dossier | null; note: string | null }) {
  if (!dossier) {
    return (
      <Card title="Annex IV technical documentation">
        <Callout tone="muted">{note ?? "Not applicable to this classification."}</Callout>
      </Card>
    );
  }
  return (
    <Card title="Annex IV technical documentation">
      <Callout tone="note">
        &quot;Validated&quot; means each citation <strong>resolves and traces</strong>{" "}
        to an obligation the classifier emitted — not that it substantiates a claim. The sections
        are a scaffold to complete.
      </Callout>
      {dossier.sections.map((s) => (
        <div key={s.number} className={sx.sectionItem}>
          <strong>
            {s.number}. {s.title}
          </strong>
          {s.citations.length > 0 ? (
            <ul className={sx.citeList}>
              {s.citations.map((cit) => (
                <li key={cit.obligation_id}>
                  <Mono>{cit.reference}</Mono> {cit.title} ({cit.effective_date})
                </li>
              ))}
            </ul>
          ) : (
            <div className={sx.meta}>No derived citations.</div>
          )}
        </div>
      ))}
    </Card>
  );
}
