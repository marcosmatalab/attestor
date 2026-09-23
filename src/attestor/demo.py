"""The end-to-end example pipeline, as a plain function.

A high-risk PROVIDER path (so Annex IV applies): classify -> Annex IV -> sign an asset
-> verify (C2PA) -> anchor in the ledger -> verify the ledger offline. Signing and
sealing use EPHEMERAL dev keys generated per call in a temp dir (never committed), so
the C2PA signer is honestly untrusted and the ledger still verifies offline.

``POST /api/demo/run`` and ``attestor demo`` both call :func:`run_demo`. It used to live
in the API routes, and the CLI reached it through FastAPI's test client - an HTTP round
trip inside one process, which dragged a test-only dependency (and its deprecation
warnings) into the first command a visitor runs. The pipeline is engine code, so it now
lives beside the engine and imports no web framework; ``tests/test_architecture.py``
keeps it that way.
"""

import base64
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.annexiv import generate_dossier
from attestor.canonical import sha256_hex
from attestor.classifier import (
    AnnexIIIArea,
    Bundle,
    Role,
    SystemProfile,
    classify,
    compare_timelines,
    load_bundle,
)
from attestor.governance import derive_crosswalk
from attestor.ledger import Ledger, verify_ledger
from attestor.ledger.keys import public_key_hex
from attestor.provenance import (
    ProvenanceMetadata,
    SignerConfig,
    generate_dev_cert,
    sign_asset,
    verify_asset,
)
from attestor.report import dump, ledger_report


def run_demo(bundle: Bundle | None = None) -> dict[str, Any]:
    """Run the example pipeline with REAL engine outputs (no mocks) and report it."""
    bundle = bundle if bundle is not None else load_bundle()
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, bundle)
    dossier = generate_dossier(profile, classification, bundle, system_name="Demo hiring system")

    with tempfile.TemporaryDirectory() as tmp:
        cert, key = Path(tmp) / "chain.pem", Path(tmp) / "key.pem"
        generate_dev_cert(cert, key)
        source, dest = Path(tmp) / "in.png", Path(tmp) / "signed.png"
        source.write_bytes(demo_png())
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
    ledger_key = Ed25519PrivateKey.generate()  # ephemeral key
    signed_root = Ledger(records).seal(ledger_key)
    # The demo sealed the ledger itself, so it knows which key to expect: pin it, the
    # way an auditor pins the operator's published key.
    ledger_result = verify_ledger(
        records, signed_root, expected_public_key=public_key_hex(ledger_key.public_key())
    )

    return {
        "profile": profile.model_dump(mode="json"),
        "classification": dump(classification, effective_dates=classification.effective_dates),
        "timeline": compare_timelines(profile).model_dump(mode="json"),
        "annex_iv": dossier.model_dump(mode="json"),
        "crosswalk": derive_crosswalk(classification).model_dump(mode="json"),
        "provenance": dump(provenance, headline=provenance.headline),
        "signed_asset_b64": base64.b64encode(signed_asset).decode("ascii"),
        "ledger": {
            "records": records,
            "signed_root": signed_root.model_dump(mode="json", exclude_none=True),
            "verification": ledger_report(ledger_result),
        },
    }


def demo_png(
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
