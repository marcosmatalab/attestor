"""Round-trip tests for the C2PA signer.

A signed asset is NOT byte-reproducible (the signature carries crypto material and
an optional timestamp), so there is no byte-identity test. Instead we read the
manifest back and assert its content semantically — including the exact AI
digitalSourceType URI.
"""

import io
import json
import struct
import zlib
from pathlib import Path

import c2pa
import pytest

from attestor.config import Settings
from attestor.provenance import ProvenanceMetadata, SignerConfig, generate_dev_cert, sign_asset
from attestor.provenance.manifest import TRAINED_ALGORITHMIC_MEDIA
from attestor.provenance.signer import build_signer


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


@pytest.fixture
def config(tmp_path: Path) -> SignerConfig:
    cert = tmp_path / "chain.pem"
    key = tmp_path / "key.pem"
    generate_dev_cert(cert, key)
    return SignerConfig(cert_path=str(cert), private_key_path=str(key))


def test_signed_asset_roundtrips_with_expected_assertions(
    config: SignerConfig, tmp_path: Path
) -> None:
    source = tmp_path / "in.png"
    source.write_bytes(_png())
    dest = tmp_path / "out.png"

    sign_asset(source, dest, config, ProvenanceMetadata(title="in.png", model="claude-opus-4-8"))

    report = json.loads(c2pa.Reader("image/png", io.BytesIO(dest.read_bytes())).json())
    manifest = report["manifests"][report["active_manifest"]]

    assert manifest["claim_generator_info"][0]["name"] == "attestor"

    # Semantic check: a c2pa.created action carrying the exact AI source-type URI.
    actions = [
        action
        for assertion in manifest["assertions"]
        if assertion["label"].startswith("c2pa.actions")
        for action in assertion["data"]["actions"]
    ]
    created = [a for a in actions if a["action"] == "c2pa.created"]
    assert any(a.get("digitalSourceType") == TRAINED_ALGORITHMIC_MEDIA for a in created)

    disclosure = next(
        a["data"] for a in manifest["assertions"] if a["label"] == "com.attestor.ai_disclosure"
    )
    assert disclosure["eu_ai_act_art50"] is True
    assert disclosure["model"] == "claude-opus-4-8"

    assert report["validation_state"] == "Valid"


def test_missing_certificate_fails_clearly(tmp_path: Path) -> None:
    config = SignerConfig(
        cert_path=str(tmp_path / "absent.pem"), private_key_path=str(tmp_path / "absent.key")
    )
    with pytest.raises(ValueError, match="certificate not found"):
        build_signer(config)


def test_signer_config_from_settings(tmp_path: Path) -> None:
    cert = tmp_path / "chain.pem"
    key = tmp_path / "key.pem"
    generate_dev_cert(cert, key)
    settings = Settings(
        c2pa_cert_path=str(cert),
        c2pa_private_key_path=str(key),
        rfc3161_tsa_url="http://tsa.example/",
    )

    config = SignerConfig.from_settings(settings)

    assert config.cert_path == str(cert)
    assert config.tsa_url == "http://tsa.example/"


def test_unconfigured_settings_raise() -> None:
    with pytest.raises(ValueError, match="C2PA signing is not configured"):
        SignerConfig.from_settings(Settings())
