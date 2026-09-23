"""HTTP endpoints — THIN wrappers over the deterministic engine.

Every endpoint calls an existing engine function and returns its output. There is NO
compliance logic here and none in the frontend: the classifier, Annex IV generator, C2PA
verifier, and ledger remain the single source of truth. Computed properties of the engine
models (``effective_dates``, ``headline``) are serialized AS-IS — never reimplemented —
so the UI shows exactly what F1-F7 produce. Gated engine errors surface as HTTP 422 with
the engine's own message.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from attestor.annexiv import generate_dossier, render_pdf
from attestor.classifier import (
    Bundle,
    Classification,
    SystemProfile,
    classify,
    compare_timelines,
    load_bundle,
)
from attestor.demo import run_demo
from attestor.governance import derive_crosswalk, generate_fria
from attestor.ledger import SignedRoot, verify_ledger
from attestor.provenance import verify_asset
from attestor.report import dump, ledger_report

router = APIRouter(prefix="/api", tags=["attestor"])

# The bundle the API serves by default: the law in force, not the text as first
# enacted. The name is kept so nothing downstream breaks.
LEGAL_TEXT_BUNDLE = "reg-2026-1744"


def _bundle() -> Bundle:
    # Loaded per request (cheap, pure); keeps the module import-time side-effect free.
    return load_bundle(LEGAL_TEXT_BUNDLE)


def _classification(profile: SystemProfile) -> Classification:
    return classify(profile, _bundle())


@router.post("/classify")
def classify_endpoint(profile: SystemProfile) -> dict[str, Any]:
    """Classify a system: risk, obligations + effective dates, and the reproducible checksum."""
    result = _classification(profile)
    return dump(result, effective_dates=result.effective_dates)


@router.post("/timeline")
def timeline_endpoint(profile: SystemProfile) -> dict[str, Any]:
    """Dual scenario: legal-text vs Digital Omnibus dates, with the provisional caveat."""
    return compare_timelines(profile).model_dump(mode="json")


@router.post("/annex-iv")
def annex_iv_endpoint(
    profile: SystemProfile, system_name: str | None = Query(default=None)
) -> dict[str, Any]:
    """Annex IV dossier for a high-risk provider classification (gated by the engine)."""
    bundle = _bundle()
    classification = classify(profile, bundle)
    try:
        dossier = generate_dossier(profile, classification, bundle, system_name=system_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return dossier.model_dump(mode="json")


@router.post("/annex-iv/pdf")
def annex_iv_pdf_endpoint(
    profile: SystemProfile, system_name: str | None = Query(default=None)
) -> Response:
    """Render the Annex IV dossier to a deterministic PDF (F3 reportlab output)."""
    bundle = _bundle()
    classification = classify(profile, bundle)
    try:
        dossier = generate_dossier(profile, classification, bundle, system_name=system_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return Response(content=render_pdf(dossier), media_type="application/pdf")


@router.post("/governance/crosswalk")
def crosswalk_endpoint(profile: SystemProfile) -> dict[str, Any]:
    """ISO/IEC 42001 reference crosswalk for the applied obligations (with disclaimer)."""
    return derive_crosswalk(_classification(profile)).model_dump(mode="json")


@router.post("/governance/fria")
def fria_endpoint(profile: SystemProfile) -> dict[str, Any]:
    """Art. 27 FRIA scaffold (gated by the engine on the art27_fria obligation)."""
    try:
        return generate_fria(profile, _classification(profile)).model_dump(mode="json")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/provenance/verify")
async def provenance_verify_endpoint(
    file: UploadFile, format: str = Query(default="image/png")
) -> dict[str, Any]:
    """Verify a C2PA-signed asset: integrity and signer trust as SEPARATE axes (F5)."""
    report = verify_asset(await file.read(), format=format)
    return dump(report, headline=report.headline)


class LedgerVerifyRequest(BaseModel):
    """Public ledger artifacts an auditor verifies offline."""

    records: list[dict[str, Any]]
    signed_root: SignedRoot
    # Raw hex of the key the ledger must be signed with, like --public-key. Without it
    # the verdict is "signer not pinned" (verified: false) unless allow_unpinned is set,
    # like --allow-unpinned.
    expected_public_key: str | None = None
    allow_unpinned: bool = False


@router.post("/ledger/verify")
def ledger_verify_endpoint(request: LedgerVerifyRequest) -> dict[str, Any]:
    """Verify a ledger offline from public artifacts (F6): tamper check vs TSA trust apart."""
    result = verify_ledger(
        request.records,
        request.signed_root,
        expected_public_key=request.expected_public_key,
        allow_unpinned=request.allow_unpinned,
    )
    return ledger_report(result)


@router.post("/demo/run")
def demo_run_endpoint() -> dict[str, Any]:
    """Run the example pipeline end to end: the same function ``attestor demo`` calls."""
    return run_demo(_bundle())
