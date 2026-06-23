"""HTTP endpoints — THIN wrappers over the deterministic engine.

Every endpoint calls an existing engine function and returns its output. There is NO
compliance logic here and none in the frontend: the classifier, Annex IV generator, C2PA
verifier, and ledger remain the single source of truth. Computed properties of the engine
models (``effective_dates``, ``headline``) are serialized AS-IS — never reimplemented —
so the UI shows exactly what F1-F7 produce. Gated engine errors surface as HTTP 422 with
the engine's own message.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
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

router = APIRouter(prefix="/api", tags=["attestor"])

LEGAL_TEXT_BUNDLE = "v2026-08"


def _bundle() -> Bundle:
    # Loaded per request (cheap, pure); keeps the module import-time side-effect free.
    return load_bundle(LEGAL_TEXT_BUNDLE)


def _dump(model: BaseModel, **computed: Any) -> dict[str, Any]:
    """Serialize an engine model plus its computed properties, verbatim."""
    return {**model.model_dump(mode="json"), **computed}


def _classification(profile: SystemProfile) -> Classification:
    return classify(profile, _bundle())


@router.post("/classify")
def classify_endpoint(profile: SystemProfile) -> dict[str, Any]:
    """Classify a system: risk, obligations + effective dates, and the reproducible checksum."""
    result = _classification(profile)
    return _dump(result, effective_dates=result.effective_dates)


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
