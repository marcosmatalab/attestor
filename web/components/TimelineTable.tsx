/** The dual-scenario table: the same obligation under each timeline.
 *
 * The caveat under the table is whatever the engine reported in `omnibus_status`,
 * which the engine in turn read from the bundle's `meta`. The literal below is a
 * fallback for the case where the API returned nothing, not a second source of
 * truth — the frontend never states the regulatory status on its own authority.
 */

import type { ObligationTimeline } from "@/lib/types";
import { getDictionary } from "@/lib/i18n/dictionaries";

export const FALLBACK_STATUS = "in force";

export interface TimelineTableProps {
  obligations: ObligationTimeline[];
  status?: string;
  locale?: string;
}

export function TimelineTable({ obligations, status, locale }: TimelineTableProps) {
  const t = getDictionary(locale);
  return (
    <div className="card">
      <table>
        <caption>{t.timeline.caption}</caption>
        <thead>
          <tr>
            <th>{t.timeline.thObligation}</th>
            <th>{t.timeline.thLegalText}</th>
            <th>{t.timeline.thOmnibus}</th>
          </tr>
        </thead>
        <tbody>
          {obligations.map((row) => {
            const diverges = row.legal_text_date !== row.omnibus_date;
            return (
              <tr key={row.id} className={diverges ? "diverges" : undefined}>
                <td>
                  <strong>{row.reference}</strong> {row.title}
                </td>
                <td className="date">{row.legal_text_date ?? t.timeline.notApplicable}</td>
                <td className="date">{row.omnibus_date ?? t.timeline.notApplicable}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="banner" style={{ marginTop: "1rem", marginBottom: 0 }}>
        {status?.trim() ? status : FALLBACK_STATUS}
      </p>
    </div>
  );
}
