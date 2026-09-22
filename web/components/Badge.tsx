/** A status pill. The tone is derived, never passed in as a colour by the caller. */

export type Tone = "high" | "ok" | "warn" | "bad";

const CLASS_BY_TONE: Record<Tone, string> = {
  high: "badge-high",
  ok: "badge-ok",
  warn: "badge-warn",
  bad: "badge-bad",
};

export function Badge({ tone, children }: { tone: Tone; children: React.ReactNode }) {
  return <span className={`badge ${CLASS_BY_TONE[tone]}`}>{children}</span>;
}

/** Risk tiers get their own scale: `high` and `prohibited` must not read as neutral. */
export function riskTone(risk: string): Tone {
  if (risk === "prohibited") return "bad";
  if (risk === "high") return "high";
  if (risk === "limited") return "warn";
  return "ok";
}
