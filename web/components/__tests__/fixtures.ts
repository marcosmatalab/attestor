/** Fixtures copied from a real POST /api/demo/run response, trimmed to what the
 *  components read. Keeping them engine-shaped means a rename on the Python side
 *  breaks these tests instead of silently breaking the page. */

import type { DemoResult, ObligationTimeline } from "@/lib/types";

export const OBLIGATIONS: ObligationTimeline[] = [
  {
    id: "art9_risk_management",
    reference: "Art. 9",
    title: "Risk management system",
    legal_text_date: "2026-08-02",
    omnibus_date: "2027-12-02",
  },
  {
    id: "art50_1_chatbot",
    reference: "Art. 50(1)",
    title: "Disclosure that a person is interacting with an AI system",
    legal_text_date: "2026-08-02",
    omnibus_date: "2026-08-02",
  },
  {
    id: "art5_ncii",
    reference: "Art. 5(1)",
    title: "NCII / CSAM prohibition",
    legal_text_date: null,
    omnibus_date: "2026-12-02",
  },
];

export const OMNIBUS_STATUS =
  "Provisional, not yet in force (as of 2026-06-23). Until then the binding timeline remains the legal-text scenario.";

export const DEMO_RESULT: DemoResult = {
  bundle: {
    version: "v2026-08",
    sha256: "7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d",
    scenario: "legal-text",
    status: "in-force",
    status_note: "",
  },
  classification: {
    risk: "high",
    checksum: "15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17",
    bundle_sha256: "7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d",
    obligations: [
      {
        id: "art9_risk_management",
        reference: "Art. 9",
        title: "Risk management system",
        effective_date: "2026-08-02",
      },
    ],
  },
  annex_iv: {
    system_name: "ACME Recruiting Screener",
    section_count: 10,
    citation_count: 14,
    dossier_sha256: "a8a5e5e3b9ccbe49b3e4613fe07e0e1f5cb69d003d1f134b66bd0fb6ff23d185",
    pdf_sha256: "78ead308c60d3c166b893db790b901dfe921b3cd3c520d1a337d03aca4f7d735",
  },
  provenance: {
    asset_sha256: "d2ccbf0f5ead37bf0000000000000000000000000000000000000000000000ff",
    validation_state: "Valid",
    integrity_ok: true,
    trusted: false,
    signer: "Attestor (development)",
    headline:
      "integrity Valid (manifest intact, claim well-formed); signer UNTRUSTED (not in a recognised C2PA trust list)",
    classification_checksum:
      "15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17",
  },
  ledger: {
    leaf_count: 3,
    signed_root: {
      merkle_root: "3e7af838a13efd15fc213ae970289c63c57bf6ad079860623208468b78d22a64",
      public_key: "289520060de76a743abb27cd1d2b07ae8030075db1fbad7e3c29426c03b0a887",
      signature: "50c888a7",
    },
    verification: {
      verified: true,
      integrity_ok: true,
      signature_ok: true,
      detail: "ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp",
    },
  },
  engine: { version: "0.0.1", llm_used: false },
};
