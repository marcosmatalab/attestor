import type { Crosswalk } from "@/lib/api";
import { Callout, Card, Mono, TableWrap } from "@/components/ui";

export function CrosswalkCard({ crosswalk }: { crosswalk: Crosswalk }) {
  return (
    <Card title="ISO/IEC 42001 crosswalk">
      <Callout tone="note">{crosswalk.disclaimer}</Callout>
      <TableWrap>
        <thead>
          <tr>
            <th scope="col">AI Act obligation</th>
            <th scope="col">Related ISO/IEC 42001 areas</th>
          </tr>
        </thead>
        <tbody>
          {crosswalk.entries.map((e) => (
            <tr key={e.obligation_id}>
              <td>
                <Mono>{e.reference}</Mono> {e.title}
              </td>
              <td>{e.iso_references.map((ref) => ref.label).join(", ")}</td>
            </tr>
          ))}
        </tbody>
      </TableWrap>
    </Card>
  );
}
