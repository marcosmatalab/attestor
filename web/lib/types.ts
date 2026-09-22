/** Shapes returned by the Attestor API. Mirrors the pydantic models on the Python side. */

export interface Obligation {
  id: string;
  reference: string;
  title: string;
  effective_date: string;
}

export interface Classification {
  risk: string;
  checksum: string;
  bundle_sha256: string;
  obligations: Obligation[];
}

export interface ObligationTimeline {
  id: string;
  reference: string;
  title: string;
  legal_text_date: string | null;
  omnibus_date: string | null;
}

export interface TimelineComparison {
  binding_scenario: string;
  legal_text_risk: string;
  omnibus_risk: string;
  omnibus_status: string;
  obligations: ObligationTimeline[];
}

export interface ProvenanceResult {
  asset_sha256: string;
  validation_state: string;
  integrity_ok: boolean;
  trusted: boolean;
  signer: string | null;
  headline: string;
  classification_checksum: string | null;
}

export interface LedgerResult {
  leaf_count: number;
  signed_root: { merkle_root: string; public_key: string; signature: string };
  verification: {
    verified: boolean;
    integrity_ok: boolean;
    signature_ok: boolean;
    detail: string;
  };
}

export interface DemoResult {
  bundle: {
    version: string;
    sha256: string;
    scenario: string | null;
    status: string | null;
    status_note: string;
  };
  classification: Classification;
  annex_iv: {
    system_name: string;
    section_count: number;
    citation_count: number;
    dossier_sha256: string;
    pdf_sha256: string;
  };
  provenance: ProvenanceResult;
  ledger: LedgerResult;
  engine: { version: string; llm_used: boolean };
}
