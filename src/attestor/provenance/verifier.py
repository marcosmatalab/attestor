"""C2PA verification (F5): integrity and trust reported as two separate axes.

This is the nuance the whole feature exists to get right. A Content Credential can
be *intact* (the manifest hashes match, the claim signature verifies, the
assertions are well formed) and at the same time signed by someone nobody
recognises. Those are different facts and collapsing them into one green tick is
how provenance tooling misleads people:

- report "invalid" for an unrecognised signer and an intact file looks tampered;
- report "valid" and an unknown signer looks endorsed.

So ``ProvenanceReport`` carries ``validation_state`` (integrity) and ``trusted``
(recognition) independently, and ``headline`` always states both. With the
development certificates this repo ships, the honest answer is *integrity Valid,
signer UNTRUSTED*, and that is what the demo prints.
"""

import json
from typing import Any

from c2pa import Reader
from pydantic import BaseModel, ConfigDict

from attestor.provenance.manifest import ATTESTOR_ASSERTION_LABEL

# C2PA validation-result codes that are about *recognition of the signer*, not
# about whether the asset is intact.
TRUST_FAILURE_CODES = frozenset(
    {
        "signingCredential.untrusted",
        "signingCredential.revoked",
        "signingCredential.expired",
        "signingCredential.invalid",
        "timeStamp.untrusted",
    }
)

UNTRUSTED_REASON = "not in a recognised C2PA trust list"


class ProvenanceReport(BaseModel):
    """What a C2PA credential does and does not prove about one asset."""

    model_config = ConfigDict(frozen=True)

    has_manifest: bool
    validation_state: str  # C2PA's own state: "Valid" | "Invalid" | "Trusted"
    integrity_ok: bool  # no non-trust failure codes
    trusted: bool  # signer recognised by a trust list
    signer: str | None
    integrity_failures: tuple[str, ...]
    trust_failures: tuple[str, ...]
    classification_checksum: str | None  # from the attestor assertion, if present
    bundle_sha256: str | None
    headline: str


def verify_bytes(asset: bytes, *, format: str = "image/png") -> ProvenanceReport:
    """Verify the Content Credential embedded in ``asset``."""
    import io

    try:
        reader = Reader(format, io.BytesIO(asset))
    except Exception as exc:  # noqa: BLE001 - any read failure means "no usable manifest"
        return _no_manifest(str(exc))
    return _report(reader)


def _no_manifest(detail: str) -> ProvenanceReport:
    return ProvenanceReport(
        has_manifest=False,
        validation_state="Unknown",
        integrity_ok=False,
        trusted=False,
        signer=None,
        integrity_failures=(),
        trust_failures=(),
        classification_checksum=None,
        bundle_sha256=None,
        headline=f"no Content Credential found ({detail})",
    )


def _report(reader: Reader) -> ProvenanceReport:
    state = str(reader.get_validation_state())
    manifest_store: dict[str, Any] = json.loads(reader.json())
    failures = _failure_codes(reader.get_validation_results())

    trust_failures = tuple(sorted(code for code in failures if code in TRUST_FAILURE_CODES))
    integrity_failures = tuple(sorted(code for code in failures if code not in TRUST_FAILURE_CODES))
    integrity_ok = not integrity_failures
    # "Trusted" is C2PA's own term for a signer that resolved against a trust list.
    trusted = state.lower() == "trusted" and not trust_failures

    active = _active_manifest(manifest_store)
    assertion = _attestor_assertion(active)

    return ProvenanceReport(
        has_manifest=active is not None,
        validation_state=state,
        integrity_ok=integrity_ok,
        trusted=trusted,
        signer=_signer_name(active),
        integrity_failures=integrity_failures,
        trust_failures=trust_failures,
        classification_checksum=assertion.get("classification_checksum"),
        bundle_sha256=assertion.get("bundle_sha256"),
        headline=_headline(state, integrity_ok, trusted, integrity_failures),
    )


def _failure_codes(results: Any) -> list[str]:
    """Collect every failure code out of C2PA's per-manifest validation results."""
    codes: list[str] = []
    if not isinstance(results, dict):
        return codes
    for per_manifest in results.values():
        if not isinstance(per_manifest, dict):
            continue
        for entry in per_manifest.get("failure", []) or []:
            if isinstance(entry, dict) and "code" in entry:
                codes.append(str(entry["code"]))
    return codes


def _active_manifest(store: dict[str, Any]) -> dict[str, Any] | None:
    label = store.get("active_manifest")
    manifests = store.get("manifests", {})
    if isinstance(manifests, dict) and isinstance(label, str):
        active = manifests.get(label)
        if isinstance(active, dict):
            return active
    return None


def _signer_name(manifest: dict[str, Any] | None) -> str | None:
    if manifest is None:
        return None
    info = manifest.get("signature_info")
    if isinstance(info, dict):
        issuer = info.get("issuer")
        if isinstance(issuer, str):
            return issuer
    return None


def _attestor_assertion(manifest: dict[str, Any] | None) -> dict[str, Any]:
    if manifest is None:
        return {}
    for assertion in manifest.get("assertions", []) or []:
        if isinstance(assertion, dict) and assertion.get("label") == ATTESTOR_ASSERTION_LABEL:
            data = assertion.get("data")
            if isinstance(data, dict):
                return data
    return {}


def _headline(
    state: str, integrity_ok: bool, trusted: bool, integrity_failures: tuple[str, ...]
) -> str:
    if integrity_ok:
        integrity = f"integrity {state} (manifest intact, claim well-formed)"
    else:
        integrity = f"integrity {state} (FAILED: {', '.join(integrity_failures)})"
    trust = "signer TRUSTED" if trusted else f"signer UNTRUSTED ({UNTRUSTED_REASON})"
    return f"{integrity}; {trust}"
