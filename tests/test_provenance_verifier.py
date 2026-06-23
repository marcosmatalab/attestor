"""Verification tests separating manifest integrity from signer trust.

The signer is reused from F4 to mint a fixture asset. The dev certificate's CA is on
no trust list, so the central assertion is: a signed asset is ``Valid`` (integrity)
AND ``untrusted`` (signer) at once — "Valid" never implies a trusted signer.

The asset is signed ONCE (module scope): signing mints a random claim URN and the dev
cert a random serial, so every signing differs. Verifying the SAME bytes, however, is
deterministic — which the reproducibility test asserts.
"""

import struct
import zlib
from pathlib import Path

import pytest

from attestor.provenance import (
    ProvenanceMetadata,
    SignerConfig,
    generate_dev_cert,
    sign_asset,
    verify_asset,
)
from attestor.provenance.manifest import TRAINED_ALGORITHMIC_MEDIA


def _png(width: int = 64, height: int = 64, rgb: tuple[int, int, int] = (120, 140, 160)) -> bytes:
    def chunk(typ: bytes, data: bytes) -> bytes:
        body = typ + data
        return (
            struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


@pytest.fixture(scope="module")
def signed_png(tmp_path_factory: pytest.TempPathFactory) -> bytes:
    """Sign one 64×64 PNG with the F4 signer and a fresh dev cert; return the bytes."""
    tmp = tmp_path_factory.mktemp("c2pa")
    cert, key = tmp / "chain.pem", tmp / "key.pem"
    generate_dev_cert(cert, key)
    source, dest = tmp / "in.png", tmp / "signed.png"
    source.write_bytes(_png())
    sign_asset(
        source,
        dest,
        SignerConfig(cert_path=str(cert), private_key_path=str(key)),
        ProvenanceMetadata(title="in.png", model="claude-opus-4-8"),
    )
    return dest.read_bytes()


def test_unsigned_asset_reports_no_manifest() -> None:
    report = verify_asset(_png(80, 80))

    assert report.has_manifest is False
    assert report.validation_state is None
    assert report.integrity_ok is False
    assert report.trusted is False  # fail-closed
    assert report.signer is None
    assert report.ai_disclosure is None
    assert report.headline == "no C2PA manifest found"


def test_signed_asset_is_valid_but_untrusted(signed_png: bytes) -> None:
    report = verify_asset(signed_png)

    assert report.has_manifest is True
    assert report.validation_state == "Valid"
    assert report.integrity_ok is True
    # Integrity OK, trust NOT — the two dimensions are independent.
    assert report.trusted is False
    assert "untrusted" in report.trust_reason.lower()


def test_valid_state_coexists_with_untrusted_failure(signed_png: bytes) -> None:
    """The concrete proof of "Valid != trusted": both hold for the same asset."""
    report = verify_asset(signed_png)

    assert report.validation_state == "Valid"
    assert report.integrity_ok is True
    assert report.validation_codes is not None
    # The untrusted signal lives in the FAILURE list while the state is still "Valid".
    assert "signingCredential.untrusted" in report.validation_codes.failure
    assert report.trusted is False


def test_signer_identity_is_reported(signed_png: bytes) -> None:
    signer = verify_asset(signed_png).signer

    assert signer is not None
    assert signer.common_name == "Attestor Dev Signer (untrusted)"
    assert signer.issuer == "Attestor Dev"
    assert signer.algorithm == "Es256"
    assert signer.cert_serial_number and signer.cert_serial_number.isdigit()


def test_ai_disclosure_is_reported(signed_png: bytes) -> None:
    disclosure = verify_asset(signed_png).ai_disclosure

    assert disclosure is not None
    assert disclosure.digital_source_type == TRAINED_ALGORITHMIC_MEDIA
    assert disclosure.ai_generated is True
    assert disclosure.eu_ai_act_art50 is True
    assert "com.attestor.ai_disclosure" in disclosure.labels


def test_tampering_breaks_integrity(signed_png: bytes) -> None:
    tampered = bytearray(signed_png)
    middle = len(tampered) // 2
    for i in range(middle, middle + 8):
        tampered[i] ^= 0xFF

    report = verify_asset(bytes(tampered))

    # Integrity fails; we assert the STATE, not a specific failure code.
    assert report.validation_state == "Invalid"
    assert report.integrity_ok is False


def test_verification_is_deterministic(signed_png: bytes) -> None:
    # Same bytes, verified twice — no per-signature random fields leak into the report.
    assert verify_asset(signed_png) == verify_asset(signed_png)


def test_verify_accepts_a_path(signed_png: bytes, tmp_path: Path) -> None:
    asset = tmp_path / "signed.png"
    asset.write_bytes(signed_png)

    assert verify_asset(asset) == verify_asset(signed_png)


def test_headline_never_states_valid_without_trust(signed_png: bytes) -> None:
    headline = verify_asset(signed_png).headline

    # Integrity and trust always appear together; "Valid" is never stated alone.
    assert "integrity Valid" in headline
    assert "UNTRUSTED" in headline
