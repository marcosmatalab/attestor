// Thin client for the Attestor backend. The frontend never computes a verdict — it
// only renders what these endpoints (themselves thin wrappers over the engine) return.

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export interface ProfileInput {
  role: "provider" | "deployer";
  annex_iii_area?: string | null;
  deployer_type?: string | null;
  annex_i_embedded?: boolean;
  is_gpai?: boolean;
  interacts_with_humans?: boolean;
  generates_synthetic_content?: boolean;
  content_lifecycle?: string | null;
}

export interface Obligation {
  id: string;
  reference: string;
  title: string;
  effective_date: string;
}

export interface Classification {
  risk: string;
  obligations: Obligation[];
  bundle_version: string;
  bundle_sha256: string;
  checksum: string;
  effective_dates: Record<string, string>;
}

export interface TimelineRow {
  id: string;
  reference: string;
  title: string;
  legal_text_date: string | null;
  omnibus_date: string | null;
}

export interface Timeline {
  binding_scenario: string;
  legal_text_risk: string;
  omnibus_risk: string;
  omnibus_status: string;
  obligations: TimelineRow[];
}

export interface Citation {
  obligation_id: string;
  reference: string;
  title: string;
  effective_date: string;
}

export interface DossierSection {
  number: string;
  title: string;
  guidance: string;
  citations: Citation[];
}

export interface Dossier {
  system_name: string;
  risk: string;
  classification_checksum: string;
  provisional_note: string;
  legal_basis: Citation | null;
  sections: DossierSection[];
}

export interface IsoReference {
  kind: string;
  id: string;
  title: string;
  label: string;
}

export interface CrosswalkEntry {
  obligation_id: string;
  reference: string;
  title: string;
  iso_references: IsoReference[];
}

export interface Crosswalk {
  risk: string;
  entries: CrosswalkEntry[];
  disclaimer: string;
}

export interface FriaSection {
  point: string;
  requirement: string;
  placeholder: string;
}

export interface Fria {
  trigger: string;
  fria_reference: string;
  fria_effective_date: string;
  sections: FriaSection[];
  notify_authority_note: string;
  disclaimer: string;
}

export interface Provenance {
  has_manifest: boolean;
  validation_state: string | null;
  integrity_ok: boolean;
  trusted: boolean;
  trust_reason: string;
  signer: { common_name: string | null; issuer: string | null; algorithm: string | null } | null;
  ai_disclosure: { digital_source_type: string | null; eu_ai_act_art50: boolean | null } | null;
  headline: string;
}

export interface LedgerVerification {
  integrity_ok: boolean;
  signature_ok: boolean;
  has_timestamp: boolean;
  verified: boolean;
  headline: string;
}

export interface DemoResult {
  classification: Classification;
  timeline: Timeline;
  annex_iv: Dossier;
  crosswalk: Crosswalk;
  provenance: Provenance;
  signed_asset_b64: string;
  ledger: {
    records: Record<string, unknown>[];
    signed_root: { merkle_root: string; leaf_count: number; signature: string };
    verification: LedgerVerification;
  };
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      if (typeof data?.detail === "string") detail = data.detail;
    } catch {
      // non-JSON error body; keep the status message
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export const api = {
  classify: (p: ProfileInput) => post<Classification>("/api/classify", p),
  timeline: (p: ProfileInput) => post<Timeline>("/api/timeline", p),
  annexIv: (p: ProfileInput) => post<Dossier>("/api/annex-iv", p),
  crosswalk: (p: ProfileInput) => post<Crosswalk>("/api/governance/crosswalk", p),
  fria: (p: ProfileInput) => post<Fria>("/api/governance/fria", p),
  demo: () => post<DemoResult>("/api/demo/run"),
};
