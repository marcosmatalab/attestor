"""HTTP surface over the engine.

The API is a thin adapter and nothing more: it validates input, calls the engine,
and serializes the result. It holds **no compliance logic** — every number a
client sees was produced by ``attestor.classifier``, ``attestor.annexiv``,
``attestor.governance``, ``attestor.provenance`` or ``attestor.ledger``.

The dependency only ever points this way. The engine packages never import
``attestor.api``, and ``tests/test_architecture.py`` enforces it, so the engine
stays usable as a library and testable without an HTTP client.
"""

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from attestor.annexiv import generate_dossier, render_pdf, validate_citations
from attestor.canonical import canonical_json, sha256_hex
from attestor.classifier import (
    SystemProfile,
    classify,
    compare_timelines,
    load_bundle,
)
from attestor.classifier.bundle import DEFAULT_VERSION, available_versions
from attestor.demo import run_demo
from attestor.governance import assess_fria, log_retention_duties, map_to_iso42001
from attestor.ledger import LedgerRecord, SignedRoot, verify_ledger

router = APIRouter(prefix="/api", tags=["attestor"])


class ClassifyRequest(BaseModel):
    """A questionnaire plus the bundle to interpret it under."""

    model_config = ConfigDict(extra="forbid")

    profile: SystemProfile
    bundle_version: str = DEFAULT_VERSION


class VerifyLedgerRequest(BaseModel):
    """A ledger submitted for offline verification."""

    model_config = ConfigDict(extra="forbid")

    records: list[LedgerRecord]
    signed_root: SignedRoot


def _load(version: str) -> Any:
    try:
        return load_bundle(version)
    except (FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=404, detail=f"unknown bundle {version!r}: {exc}") from exc


@router.get("/bundles")
def list_bundles() -> dict[str, Any]:
    """The regulatory bundles this build ships, with their content hashes."""
    bundles = []
    for version in available_versions():
        bundle = load_bundle(version)
        bundles.append(
            {
                "version": bundle.version,
                "sha256": bundle.sha256,
                "scenario": bundle.meta.get("scenario"),
                "status": bundle.meta.get("status"),
                "status_note": str(bundle.meta.get("status_note", "")).strip(),
            }
        )
    return {"default": DEFAULT_VERSION, "bundles": bundles}


@router.post("/classify")
def post_classify(request: ClassifyRequest) -> dict[str, Any]:
    """Classify a profile deterministically under one bundle."""
    bundle = _load(request.bundle_version)
    result = classify(request.profile, bundle)
    return result.model_dump(mode="json")


@router.post("/timeline")
def post_timeline(profile: SystemProfile) -> dict[str, Any]:
    """Compare the same profile across the shipped timeline scenarios."""
    return compare_timelines(profile).model_dump(mode="json")


@router.post("/annex-iv")
def post_annex_iv(request: ClassifyRequest) -> dict[str, Any]:
    """Generate the Annex IV dossier and validate every citation (fail-closed)."""
    bundle = _load(request.bundle_version)
    classification = classify(request.profile, bundle)
    try:
        dossier = generate_dossier(request.profile, classification, bundle)
        validate_citations(dossier, classification, bundle)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    payload = dossier.model_dump(mode="json")
    return {
        "dossier": payload,
        "dossier_sha256": sha256_hex(canonical_json(payload)),
        "pdf_sha256": sha256_hex(render_pdf(dossier)),
    }


@router.post("/governance")
def post_governance(request: ClassifyRequest) -> dict[str, Any]:
    """The ISO/IEC 42001 map, the Art. 27 FRIA scaffold and the log-retention duties."""
    bundle = _load(request.bundle_version)
    classification = classify(request.profile, bundle)
    return {
        "iso42001": map_to_iso42001(classification).model_dump(mode="json"),
        "fria": assess_fria(classification).model_dump(mode="json"),
        "log_retention": [d.model_dump(mode="json") for d in log_retention_duties(classification)],
    }


@router.post("/ledger/verify")
def post_verify_ledger(request: VerifyLedgerRequest) -> dict[str, Any]:
    """Verify a submitted ledger. Same code path the offline CLI uses."""
    return verify_ledger(request.records, request.signed_root).model_dump(mode="json")


@router.post("/demo/run")
def post_demo_run() -> dict[str, Any]:
    """Run the full pipeline end to end, with no keys and no network."""
    return run_demo()
