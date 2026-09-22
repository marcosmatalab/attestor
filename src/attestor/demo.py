"""The end-to-end pipeline, in one place, shared by the API and the CLI.

Classify -> Annex IV dossier -> C2PA-sign an output -> anchor all three in the
ledger -> verify the ledger offline. It runs with **no keys and no network**: the
signing material is generated in memory for the run and thrown away.

What is deterministic here, and what is not, is a deliberate line — and it is
drawn where the cryptography actually draws it, not where it would look best:

- deterministic: the classification checksum, the bundle hash, the Annex IV
  dossier and its PDF. Same clone, same machine, same values, forever.
- **not** deterministic: the C2PA-signed asset. The demo mints an ephemeral
  certificate and ECDSA signing is randomised, so the signed bytes — and therefore
  the digest anchored as ``rec-3``, and therefore the Merkle root and the Ed25519
  signature over it — differ on every run.

That is the honest cost of committing no private key, and it is why
``tests/test_demo_snapshot.py`` pins the first group and excludes the second
rather than pretending the whole report is reproducible. ``RECORDED_AT`` is still
a fixed constant instead of the wall clock, so the only thing that moves between
two runs is what the ephemeral key made move.
"""

from datetime import UTC, datetime
from typing import Any

from attestor import __version__
from attestor.annexiv import generate_dossier, render_pdf, validate_citations
from attestor.canonical import canonical_json, sha256_hex
from attestor.classifier import (
    AnnexIIIArea,
    Classification,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)
from attestor.governance import assess_fria, log_retention_duties, map_to_iso42001
from attestor.ledger import Ledger, ledger_key_from_settings, save_ledger, verify_ledger
from attestor.ledger.model import LedgerRecord, LedgerVerification, SignedRoot
from attestor.provenance import (
    ProvenanceReport,
    build_manifest,
    build_signer,
    sign_bytes,
    signing_material_from_settings,
    synthetic_png,
    verify_bytes,
)

DEMO_SYSTEM_NAME = "ACME Recruiting Screener"
DEMO_SUBJECT = "sys-1"
DEMO_ASSET_TITLE = "attestor-demo.png"
# Fixed so the Merkle root is reproducible; see the module docstring.
RECORDED_AT = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)


def demo_profile() -> SystemProfile:
    """The profile the demo classifies: a provider of an Annex III employment system."""
    return SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)


def run_demo(bundle_version: str | None = None) -> dict[str, Any]:
    """Run the whole pipeline and return a JSON-serializable report."""
    bundle = load_bundle(bundle_version) if bundle_version else load_bundle()
    profile = demo_profile()
    classification = classify(profile, bundle)

    dossier = generate_dossier(profile, classification, bundle, system_name=DEMO_SYSTEM_NAME)
    validate_citations(dossier, classification, bundle)
    dossier_sha256 = sha256_hex(canonical_json(dossier.model_dump(mode="json")))
    pdf_sha256 = sha256_hex(render_pdf(dossier))

    signed_asset, provenance = _sign_and_verify(classification)
    asset_sha256 = sha256_hex(signed_asset)

    records, signed_root, verification = _anchor(
        classification.checksum, dossier_sha256, asset_sha256
    )

    return {
        "bundle": {
            "version": bundle.version,
            "sha256": bundle.sha256,
            "scenario": bundle.meta.get("scenario"),
            "status": bundle.meta.get("status"),
            "status_note": str(bundle.meta.get("status_note", "")).strip(),
        },
        "classification": {
            "risk": classification.risk.value,
            "checksum": classification.checksum,
            "bundle_sha256": classification.bundle_sha256,
            "obligations": [
                {
                    "id": o.id,
                    "reference": o.reference,
                    "title": o.title,
                    "effective_date": o.effective_date.isoformat(),
                }
                for o in classification.obligations
            ],
        },
        "annex_iv": {
            "system_name": dossier.system_name,
            "section_count": len(dossier.sections),
            "citation_count": len(dossier.all_citations),
            "dossier_sha256": dossier_sha256,
            "pdf_sha256": pdf_sha256,
        },
        "governance": _governance_view(classification),
        "provenance": {
            "asset_sha256": asset_sha256,
            "validation_state": provenance.validation_state,
            "integrity_ok": provenance.integrity_ok,
            "trusted": provenance.trusted,
            "signer": provenance.signer,
            "headline": provenance.headline,
            "classification_checksum": provenance.classification_checksum,
        },
        "ledger": {
            "leaf_count": signed_root.leaf_count,
            "records": [r.model_dump(mode="json") for r in records],
            "signed_root": signed_root.model_dump(mode="json", exclude_none=True),
            "verification": {
                "verified": verification.verified,
                "integrity_ok": verification.integrity_ok,
                "signature_ok": verification.signature_ok,
                "detail": verification.detail,
            },
        },
        "engine": {"version": __version__, "llm_used": False},
    }


def _sign_and_verify(classification: Classification) -> tuple[bytes, ProvenanceReport]:
    manifest = build_manifest(classification, title=DEMO_ASSET_TITLE, version=__version__)
    signer = build_signer(signing_material_from_settings())
    signed_asset = sign_bytes(manifest, synthetic_png(), signer)
    return signed_asset, verify_bytes(signed_asset)


def _anchor(
    classification_checksum: str, dossier_sha256: str, asset_sha256: str
) -> tuple[list[LedgerRecord], SignedRoot, LedgerVerification]:
    ledger = Ledger()
    ledger.append(
        id="rec-1",
        kind="classification",
        subject=DEMO_SUBJECT,
        payload_sha256=classification_checksum,
        recorded_at=RECORDED_AT,
    )
    ledger.append(
        id="rec-2",
        kind="annex-iv-dossier",
        subject=DEMO_SUBJECT,
        payload_sha256=dossier_sha256,
        recorded_at=RECORDED_AT,
    )
    ledger.append(
        id="rec-3",
        kind="c2pa-manifest",
        subject=DEMO_SUBJECT,
        payload_sha256=asset_sha256,
        recorded_at=RECORDED_AT,
    )
    signed_root = ledger.seal(ledger_key_from_settings(), sealed_at=RECORDED_AT)
    return ledger.records, signed_root, verify_ledger(ledger.records, signed_root)


def _governance_view(classification: Classification) -> dict[str, Any]:
    iso = map_to_iso42001(classification)
    fria = assess_fria(classification)
    return {
        "iso42001_clauses": list(iso.clauses),
        "iso42001_mapped": len(iso.mappings),
        "iso42001_unmapped": list(iso.unmapped_obligations),
        "fria_required": fria.required,
        "fria_reason": fria.reason,
        "log_retention": [
            {"reference": d.reference, "minimum_retention_months": d.minimum_retention_months}
            for d in log_retention_duties(classification)
        ],
    }


def write_demo_ledger(directory: str) -> SignedRoot:
    """Run the demo and persist its ledger to ``directory`` (used by scripts)."""
    report = run_demo()
    records = [LedgerRecord.model_validate(r) for r in report["ledger"]["records"]]
    root = SignedRoot.model_validate(report["ledger"]["signed_root"])
    save_ledger(directory, records, root)
    return root
