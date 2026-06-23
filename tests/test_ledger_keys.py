"""Tests for Ed25519 ledger key management."""

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.config import Settings
from attestor.ledger import (
    LedgerKeyConfig,
    generate_ledger_key,
    load_private_key,
    load_public_key_hex,
    public_key_hex,
)


def test_generate_and_load_roundtrips(tmp_path: Path) -> None:
    key_path = tmp_path / "ledger.key"
    generate_ledger_key(key_path)

    key = load_private_key(key_path)
    assert isinstance(key, Ed25519PrivateKey)


def test_signature_is_deterministic(tmp_path: Path) -> None:
    key_path = tmp_path / "ledger.key"
    generate_ledger_key(key_path)
    key = load_private_key(key_path)

    # RFC 8032: same key + message -> identical 64-byte signature.
    first = key.sign(b"attestor-root")
    second = key.sign(b"attestor-root")
    assert first == second
    assert len(first) == 64


def test_public_key_hex_roundtrips(tmp_path: Path) -> None:
    key_path = tmp_path / "ledger.key"
    generate_ledger_key(key_path)
    key = load_private_key(key_path)

    hex_key = public_key_hex(key.public_key())
    assert len(bytes.fromhex(hex_key)) == 32

    # The published hex rebuilds a public key that verifies the private key's signature.
    rebuilt = load_public_key_hex(hex_key)
    rebuilt.verify(key.sign(b"msg"), b"msg")


def test_missing_key_fails_clearly(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="signing key not found"):
        load_private_key(tmp_path / "absent.key")


def test_non_ed25519_key_rejected(tmp_path: Path) -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    key_path = tmp_path / "ec.key"
    key_path.write_bytes(
        ec.generate_private_key(ec.SECP256R1()).private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    with pytest.raises(ValueError, match="must be an Ed25519"):
        load_private_key(key_path)


def test_config_from_settings(tmp_path: Path) -> None:
    config = LedgerKeyConfig.from_settings(Settings(ledger_signing_key_path=str(tmp_path / "k")))
    assert config.private_key_path == str(tmp_path / "k")


def test_unconfigured_settings_raise() -> None:
    with pytest.raises(ValueError, match="Ledger signing is not configured"):
        LedgerKeyConfig.from_settings(Settings())
