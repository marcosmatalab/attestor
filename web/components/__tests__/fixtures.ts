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
  "In force. Regulation (EU) 2026/1744 (Digital Omnibus on AI) was adopted by the Council on 2026-06-29, published in the Official Journal on 2026-07-24, and entered into force on 2026-07-27.";

export const DEMO_RESULT: DemoResult = {
  bundle: {
    version: "reg-2026-1744",
    sha256: "6a8cba0a08bcf03868224155c0af24fda24973a3aade595be0e1f7ae563f2c1a",
    scenario: "in-force",
    status: "in-force",
    status_note: "In force since 2026-07-27.",
  },
  classification: {
    risk: "high",
    checksum: "d821e3e0b95d4edda4416916f2a5b02ef0296f34704a0010ee0222b3a9e0ee48",
    bundle_sha256: "6a8cba0a08bcf03868224155c0af24fda24973a3aade595be0e1f7ae563f2c1a",
    obligations: [
      {
        id: "art9_risk_management",
        reference: "Art. 9",
        title: "Risk management system",
        effective_date: "2027-12-02",
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
      "d821e3e0b95d4edda4416916f2a5b02ef0296f34704a0010ee0222b3a9e0ee48",
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
