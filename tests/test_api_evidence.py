"""Tests for the governance, provenance, ledger, and end-to-end demo endpoints.

As with the core endpoints, the responses must equal direct engine calls — and the
provenance/ledger honesty nuances (untrusted dev signer, tamper detection) must survive
the HTTP layer unchanged.
"""

import struct
import zlib
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from attestor.api.main import app
from attestor.classifier import SystemProfile, classify, load_bundle
from attestor.governance import derive_crosswalk
from attestor.ledger import Ledger
from attestor.provenance import (
    ProvenanceMetadata,
    SignerConfig,
    generate_dev_cert,
    sign_asset,
)

client = TestClient(app)
_BUNDLE = load_bundle("v2026-08")
_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _png(width: int = 64, height: int = 64) -> bytes:
    def chunk(typ: bytes, data: bytes) -> bytes:
        body = typ + data
        crc = zlib.crc32(body) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + body + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes((120, 140, 160)) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def _signed_png(tmp_path: Path) -> bytes:
    cert, key = tmp_path / "chain.pem", tmp_path / "key.pem"
    generate_dev_cert(cert, key)
    source, dest = tmp_path / "in.png", tmp_path / "out.png"
    source.write_bytes(_png())
    sign_asset(
        source,
        dest,
        SignerConfig(cert_path=str(cert), private_key_path=str(key)),
        ProvenanceMetadata(title="t", model="m"),
    )
    return dest.read_bytes()


def test_crosswalk_matches_the_engine() -> None:
    profile = {"role": "provider", "annex_iii_area": "employment"}
    body = client.post("/api/governance/crosswalk", json=profile).json()

    direct = derive_crosswalk(classify(SystemProfile(**profile), _BUNDLE))
    assert len(body["entries"]) == len(direct.entries)
    assert "not an audit" in body["disclaimer"].lower()


def test_fria_generates_and_is_gated() -> None:
    deployer = {"role": "deployer", "deployer_type": "public_body", "annex_iii_area": "employment"}
    ok = client.post("/api/governance/fria", json=deployer)
    assert ok.status_code == 200
    assert len(ok.json()["sections"]) == 6

    # A provider draws no FRIA -> the engine's gate surfaces as 422.
    provider = {"role": "provider", "annex_iii_area": "employment"}
    gated = client.post("/api/governance/fria", json=provider)
    assert gated.status_code == 422
    assert "does not apply" in gated.json()["detail"]


def test_provenance_verify_keeps_the_integrity_vs_trust_nuance(tmp_path: Path) -> None:
    signed = _signed_png(tmp_path)
    body = client.post(
        "/api/provenance/verify", files={"file": ("signed.png", signed, "image/png")}
    ).json()

    assert body["validation_state"] == "Valid"  # integrity
    assert body["trusted"] is False  # ...but the dev signer is untrusted
    assert "UNTRUSTED" in body["headline"]  # "Valid" never appears without the qualifier


def test_ledger_verify_detects_tampering() -> None:
    records = [{"type": "classification", "checksum": "abc"}, {"type": "c2pa", "sha256": "def"}]
    signed_root = Ledger(records).seal(_TEST_KEY).model_dump(mode="json", exclude_none=True)

    ok = client.post("/api/ledger/verify", json={"records": records, "signed_root": signed_root})
    assert ok.json()["verified"] is True

    tampered = [{"type": "classification", "checksum": "XXX"}, records[1]]
    bad = client.post("/api/ledger/verify", json={"records": tampered, "signed_root": signed_root})
    assert bad.json()["verified"] is False  # tamper-evident through the HTTP layer


def test_demo_run_returns_real_outputs() -> None:
    body = client.post("/api/demo/run").json()

    # Classification checksum equals a direct engine call -> the demo is real, not scripted.
    direct = classify(SystemProfile(role="provider", annex_iii_area="employment"), _BUNDLE)
    assert body["classification"]["checksum"] == direct.checksum
    # C2PA: integrity valid but signer honestly untrusted.
    assert body["provenance"]["trusted"] is False
    assert "UNTRUSTED" in body["provenance"]["headline"]
    # Ledger anchoring the run verifies offline.
    assert body["ledger"]["verification"]["verified"] is True
    assert body["signed_asset_b64"]
