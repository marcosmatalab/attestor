"""HTTP endpoints — THIN wrappers over the deterministic engine.

Every endpoint calls an existing engine function and returns its output. There is NO
compliance logic here and none in the frontend: the classifier, Annex IV generator, C2PA
verifier, and ledger remain the single source of truth. Computed properties of the engine
models (``effective_dates``, ``headline``) are serialized AS-IS — never reimplemented —
so the UI shows exactly what F1-F7 produce. Gated engine errors surface as HTTP 422 with
the engine's own message.
"""

import base64
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from attestor.annexiv import generate_dossier, render_pdf
from attestor.canonical import sha256_hex
from attestor.classifier import (
    Bundle,
    Classification,
    SystemProfile,
    classify,
    compare_timelines,
    load_bundle,
)
from attestor.governance import derive_crosswalk, generate_fria
from attestor.ledger import Ledger, SignedRoot, verify_ledger
from attestor.provenance import (
    ProvenanceMetadata,
    SignerConfig,
    generate_dev_cert,
    sign_asset,
    verify_asset,
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
    return _dump(report, headline=report.headline)


class LedgerVerifyRequest(BaseModel):
    """Public ledger artifacts an auditor verifies offline."""

    records: list[dict[str, Any]]
    signed_root: SignedRoot


@router.post("/ledger/verify")
def ledger_verify_endpoint(request: LedgerVerifyRequest) -> dict[str, Any]:
    """Verify a ledger offline from public artifacts (F6): tamper check vs TSA trust apart."""
    result = verify_ledger(request.records, request.signed_root)
    return _dump(result, headline=result.headline, verified=result.verified)


@router.post("/demo/run")
def demo_run_endpoint() -> dict[str, Any]:
    """Run one example pipeline end-to-end with REAL engine outputs (no mocks).

    A high-risk PROVIDER path (so Annex IV applies): classify -> Annex IV -> sign an asset
    -> verify (C2PA) -> anchor in the ledger -> verify the ledger offline. Signing and
    sealing use EPHEMERAL dev keys generated per request in a temp dir (never committed),
    so the C2PA signer is honestly untrusted and the ledger still verifies offline.
    """
    bundle = _bundle()
    profile = SystemProfile(role="provider", annex_iii_area="employment")
    classification = classify(profile, bundle)
    dossier = generate_dossier(profile, classification, bundle, system_name="Demo hiring system")

    with tempfile.TemporaryDirectory() as tmp:
        cert, key = Path(tmp) / "chain.pem", Path(tmp) / "key.pem"
        generate_dev_cert(cert, key)
        source, dest = Path(tmp) / "in.png", Path(tmp) / "signed.png"
        source.write_bytes(_demo_png())
        sign_asset(
            source,
            dest,
            SignerConfig(cert_path=str(cert), private_key_path=str(key)),
            ProvenanceMetadata(title="demo output", model="claude-opus-4-8"),
        )
        signed_asset = dest.read_bytes()

    provenance = verify_asset(signed_asset)

    records: list[dict[str, Any]] = [
        {"type": "classification", "checksum": classification.checksum},
        {"type": "annex_iv", "classification_checksum": dossier.classification_checksum},
        {"type": "c2pa_manifest", "sha256": sha256_hex(signed_asset)},
    ]
    signed_root = Ledger(records).seal(Ed25519PrivateKey.generate())  # ephemeral key
    ledger_result = verify_ledger(records, signed_root)

    return {
        "profile": profile.model_dump(mode="json"),
        "classification": _dump(classification, effective_dates=classification.effective_dates),
        "timeline": compare_timelines(profile).model_dump(mode="json"),
        "annex_iv": dossier.model_dump(mode="json"),
        "crosswalk": derive_crosswalk(classification).model_dump(mode="json"),
        "provenance": _dump(provenance, headline=provenance.headline),
        "signed_asset_b64": base64.b64encode(signed_asset).decode("ascii"),
        "ledger": {
            "records": records,
            "signed_root": signed_root.model_dump(mode="json", exclude_none=True),
            "verification": _dump(
                ledger_result, headline=ledger_result.headline, verified=ledger_result.verified
            ),
        },
    }


def _demo_png(
    width: int = 64, height: int = 64, rgb: tuple[int, int, int] = (120, 140, 160)
) -> bytes:
    """A minimal valid PNG (stdlib only) to stand in for an AI-generated output."""

    def chunk(typ: bytes, data: bytes) -> bytes:
        body = typ + data
        crc = zlib.crc32(body) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
