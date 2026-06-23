import type { Classification } from "@/lib/api";
import { Badge, Card, KeyValue, KV, Mono, TableWrap, type Tone } from "@/components/ui";
import sx from "./sections.module.css";

const RISK_TONE: Record<string, Tone> = {
  prohibited: "prohibited",
  high: "high",
  limited: "limited",
  minimal: "minimal",
};

export function ClassificationCard({ c }: { c: Classification }) {
  return (
    <Card title="Classification">
      <div className={sx.badgeRow}>
        <Badge tone={RISK_TONE[c.risk] ?? "neutral"}>{c.risk}</Badge>
      </div>
      <KeyValue>
        <KV k="Bundle">
          {c.bundle_version} <Mono>({c.bundle_sha256.slice(0, 16)}…)</Mono>
        </KV>
        <KV k="Reproducible checksum">
          <Mono>{c.checksum}</Mono>
        </KV>
      </KeyValue>
      <TableWrap caption="Applicable obligations and their legal-text effective dates">
        <thead>
          <tr>
            <th scope="col">Obligation</th>
            <th scope="col">Reference</th>
            <th scope="col">Effective (legal text)</th>
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
