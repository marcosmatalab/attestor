"""C2PA verification: separate manifest INTEGRITY from signer TRUST.

A signed asset has two independent properties a verifier must never conflate:

* **Integrity** — is the manifest intact and the claim well-formed? This is the
  ``validation_state`` ("Valid"/"Invalid"). "Valid" means the bytes covered by the
  claim have not changed and the claim signature verifies — nothing more.
* **Trust** — is the *signer* recognised? The certificate chains to a CA on a C2PA
  trust list, or it does not. This is reported SEPARATELY, via the
  ``signingCredential.trusted`` / ``signingCredential.untrusted`` validation code.

The two coexist. Attestor's development certificate produces ``validation_state ==
"Valid"`` AND a ``signingCredential.untrusted`` entry in the *failure* list — concrete
proof that "Valid" does not mean "trusted". Trust is fail-closed: a signer is reported
untrusted unless a trust anchor is configured and the chain validates against it.
Configuring a trust list is a deployment concern; F5 ships none, so the dev signer is
always untrusted. Verification is deterministic: the same bytes yield the same report.
"""

import io
import json
from pathlib import Path
from typing import Any

import c2pa

from attestor.provenance.report import (
    AiDisclosure,
    SignerIdentity,
    ValidationCodes,
    VerificationReport,
)

# Validation states meaning the manifest is intact and the claim well-formed.
_INTEGRITY_OK_STATES = frozenset({"Valid", "Trusted"})
# Validation-result codes carrying the signer-trust signal (separate from integrity).
_TRUST_CODE_PREFIX = "signingCredential."
_TRUSTED_CODE = "signingCredential.trusted"

# Standard C2PA actions assertion (v2) and Attestor's custom AI-disclosure assertion.
_ACTIONS_LABEL = "c2pa.actions.v2"
_DISCLOSURE_LABEL = "com.attestor.ai_disclosure"


def verify_asset(source: str | Path | bytes, *, format: str = "image/png") -> VerificationReport:
    """Read a (possibly signed) asset and report its integrity and signer trust.

    Verification is deterministic: identical bytes always yield an identical report.
    An unsigned asset yields ``has_manifest=False`` without raising.
    """
    data = source if isinstance(source, bytes) else Path(source).read_bytes()
    try:
        reader = c2pa.Reader(format, io.BytesIO(data))
    except c2pa.C2paError as exc:
        if _is_manifest_not_found(exc):
            return VerificationReport(has_manifest=False, trust_reason="no C2PA manifest present")
        raise

    active = _active_manifest(json.loads(reader.json()))
    codes = _collect_codes(reader)
    state = reader.get_validation_state()
    trusted, trust_reason = _assess_trust(state, codes)
    return VerificationReport(
        has_manifest=True,
        validation_state=state,
        integrity_ok=state in _INTEGRITY_OK_STATES,
        trusted=trusted,
        trust_reason=trust_reason,
        signer=_signer(active),
        ai_disclosure=_ai_disclosure(active),
        validation_codes=codes,
    )


def _is_manifest_not_found(exc: c2pa.C2paError) -> bool:
    """Distinguish "no manifest present" from other C2PA errors (which propagate)."""
    return "ManifestNotFound" in type(exc).__name__ or str(exc).startswith("ManifestNotFound")


def _active_manifest(report: dict[str, Any]) -> dict[str, Any]:
    manifests = report.get("manifests", {})
    active_label = report.get("active_manifest")
    if active_label in manifests:
        return manifests[active_label]
    return next(iter(manifests.values()), {})


def _collect_codes(reader: c2pa.Reader) -> ValidationCodes:
    active = (reader.get_validation_results() or {}).get("activeManifest", {})

    def codes(category: str) -> tuple[str, ...]:
        return tuple(entry["code"] for entry in active.get(category, []) if "code" in entry)

    return ValidationCodes(
        success=codes("success"),
        informational=codes("informational"),
        failure=codes("failure"),
    )


def _assess_trust(state: str | None, codes: ValidationCodes) -> tuple[bool, str]:
    """Decide signer trust, fail-closed, citing only a code that is actually present."""
    if state == "Trusted" or _TRUSTED_CODE in codes.success:
        return True, "signer chains to a configured trust anchor"
    trust_codes = [
        code
        for code in (*codes.success, *codes.informational, *codes.failure)
        if code.startswith(_TRUST_CODE_PREFIX)
    ]
    if trust_codes:
        return False, f"{trust_codes[0]}: signing certificate not on any configured trust list"
    return False, "trust not established (no trust anchor configured)"


def _signer(active: dict[str, Any]) -> SignerIdentity | None:
    info = active.get("signature_info")
    if not info:
        return None
    return SignerIdentity(
        common_name=info.get("common_name"),
        issuer=info.get("issuer"),
        cert_serial_number=info.get("cert_serial_number"),
        algorithm=info.get("alg"),
    )


def _ai_disclosure(active: dict[str, Any]) -> AiDisclosure | None:
    assertions = active.get("assertions", [])
    labels = tuple(a["label"] for a in assertions if a.get("label"))
    if not labels:
        return None

    digital_source_type = ai_generated = eu_ai_act_art50 = None
    for assertion in assertions:
        data = assertion.get("data", {})
        if assertion.get("label") == _ACTIONS_LABEL:
            for action in data.get("actions", []):
                if "digitalSourceType" in action:
                    digital_source_type = action["digitalSourceType"]
        elif assertion.get("label") == _DISCLOSURE_LABEL:
            ai_generated = data.get("ai_generated")
            eu_ai_act_art50 = data.get("eu_ai_act_art50")

    return AiDisclosure(
        ai_generated=ai_generated,
        digital_source_type=digital_source_type,
        eu_ai_act_art50=eu_ai_act_art50,
        labels=labels,
    )
