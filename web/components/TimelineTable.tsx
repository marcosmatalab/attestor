import type { Timeline } from "@/lib/api";
import { Callout, Card, Mono, TableWrap, cellDiverges } from "@/components/ui";

export function TimelineTable({ t }: { t: Timeline }) {
  return (
    <Card title="Dual timeline — legal text vs Digital Omnibus">
      <Callout tone="caveat">
        The binding legal text remains Reg. (EU) 2024/1689. The Omnibus column is provisional:{" "}
        {t.omnibus_status || "pending formal adoption"}. Both dates are shown — never one as
        &quot;the&quot; date.
      </Callout>
      <TableWrap>
        <thead>
          <tr>
            <th scope="col">Obligation</th>
            <th scope="col">Legal text</th>
            <th scope="col">Omnibus (provisional)</th>
          </tr>
        </thead>
        <tbody>
          {t.obligations.map((o) => {
            const diverges = o.legal_text_date !== o.omnibus_date;
            return (
              <tr key={o.id}>
                <td>
                  <Mono>{o.reference}</Mono> {o.title}
                </td>
                <td>{o.legal_text_date ?? "—"}</td>
                <td className={diverges ? cellDiverges : undefined}>{o.omnibus_date ?? "—"}</td>
              </tr>
            );
          })}
        </tbody>
      </TableWrap>
    </Card>
  );
}
