// Engine-shaped fixtures. Tests pass these to components and assert the UI shows exactly
// what the engine produced — never a fabricated verdict or computed score.
import type { Classification, Provenance, Timeline } from "@/lib/api";

export function provenance(trusted: boolean): Provenance {
  return {
    has_manifest: true,
    validation_state: "Valid",
    integrity_ok: true,
    trusted,
    trust_reason: trusted
      ? "signer chains to a configured trust anchor"
      : "signingCredential.untrusted: signing certificate not on any configured trust list",
    signer: {
      common_name: "Attestor Dev Signer (untrusted)",
      issuer: "Attestor Dev",
      algorithm: "Es256",
    },
    ai_disclosure: {
      digital_source_type: "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
      eu_ai_act_art50: true,
    },
    headline: trusted
      ? "integrity Valid (manifest intact, claim well-formed); signer TRUSTED"
      : "integrity Valid (manifest intact, claim well-formed); signer UNTRUSTED — signingCredential.untrusted",
  };
}

export function classification(checksum: string): Classification {
  return {
    risk: "high",
    obligations: [
      {
        id: "art9_risk_management",
        reference: "Art. 9",
        title: "Risk management system",
        effective_date: "2026-08-02",
      },
    ],
    bundle_version: "v2026-08",
    bundle_sha256: "abc123def456abc1",
    checksum,
    effective_dates: { art9_risk_management: "2026-08-02" },
  };
}

export function timeline(): Timeline {
  return {
    binding_scenario: "legal-text",
    legal_text_risk: "high",
    omnibus_risk: "high",
    omnibus_status: "pending formal adoption (provisional)",
    obligations: [
      {
        id: "art9_risk_management",
        reference: "Art. 9",
        title: "Risk management system",
        legal_text_date: "2026-08-02",
        omnibus_date: "2027-12-02",
      },
    ],
  };
}
