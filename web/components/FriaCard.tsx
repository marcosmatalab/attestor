import type { Fria } from "@/lib/api";
import { Callout, Card, Mono } from "@/components/ui";
import sx from "./sections.module.css";

export function FriaCard({ fria, note }: { fria: Fria | null; note: string | null }) {
  if (!fria) {
    return (
      <Card title="FRIA — fundamental rights impact assessment (Art. 27)">
        <Callout tone="muted">{note ?? "Not applicable to this classification."}</Callout>
      </Card>
    );
  }
  return (
    <Card title="FRIA scaffold (Art. 27)">
      <p className={sx.meta}>
        Trigger: {fria.trigger} · {fria.fria_reference}, effective {fria.fria_effective_date}
      </p>
      <Callout tone="caveat">{fria.disclaimer}</Callout>
      <ul className={sx.citeList}>
        {fria.sections.map((s) => (
          <li key={s.point}>
            <strong>({s.point})</strong> {s.requirement}
            <div className={sx.meta}>
              <Mono>{s.placeholder}</Mono>
            </div>
          </li>
        ))}
      </ul>
      <p className={sx.fineprint}>{fria.notify_authority_note}</p>
    </Card>
  );
}
