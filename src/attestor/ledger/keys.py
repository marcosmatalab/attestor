"""Ed25519 signing keys for the ledger.

The private key signs Merkle roots; it lives in config (``LEDGER_SIGNING_KEY_PATH``),
never committed. The public key is published so third parties can verify offline — the
verifier needs only the public key, never the private one. Ed25519 signatures are
deterministic (RFC 8032): the same key and message always produce the same 64-byte
signature, part of the ledger's reproducibility contract. FOR DEVELOPMENT the key can be
generated locally, and the path is config-driven; a KMS/HSM signer would replace
this loader. No such backend is implemented here.
"""

import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from pydantic import BaseModel, ConfigDict

from attestor.config import Settings

_PEM = serialization.Encoding.PEM
_RAW = serialization.Encoding.Raw


class LedgerKeyConfig(BaseModel):
    """Where the Ed25519 signing key lives (the private key, never committed)."""

    model_config = ConfigDict(frozen=True)

    private_key_path: str

    @classmethod
    def from_settings(cls, settings: Settings) -> "LedgerKeyConfig":
        if not settings.ledger_signing_key_path:
            raise ValueError(
                "Ledger signing is not configured: set LEDGER_SIGNING_KEY_PATH "
                "(generate a dev key with generate_ledger_key)"
            )
        return cls(private_key_path=settings.ledger_signing_key_path)


def generate_ledger_key(private_key_path: str | Path) -> None:
    """Write a fresh Ed25519 private key (PKCS8 PEM). FOR DEVELOPMENT ONLY; never commit."""
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(_PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    Path(private_key_path).write_bytes(pem)


def load_private_key(private_key_path: str | Path) -> Ed25519PrivateKey:
    """Load the Ed25519 signing key from ``private_key_path`` (fail-closed on type)."""
    resolved = Path(private_key_path)
    if not resolved.is_file():
        raise ValueError(f"Ledger signing key not found at {resolved}")
    key = serialization.load_pem_private_key(resolved.read_bytes(), password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Ledger signing key must be an Ed25519 private key")
    return key


def public_key_hex(public_key: Ed25519PublicKey) -> str:
    """Return the 32-byte raw Ed25519 public key as hex (the published verifier input)."""
    return public_key.public_bytes(_RAW, serialization.PublicFormat.Raw).hex()


def load_public_key_hex(hex_key: str) -> Ed25519PublicKey:
    """Rebuild an Ed25519 public key from its 32-byte hex (an offline verifier input)."""
    return Ed25519PublicKey.from_public_bytes(bytes.fromhex(hex_key))


def public_key_fingerprint(hex_key: str) -> str:
    """SHA-256 of the raw 32-byte key: short enough to publish and compare by eye."""
    return hashlib.sha256(bytes.fromhex(hex_key)).hexdigest()


def public_key_pem(hex_key: str) -> bytes:
    """The key as a standard SubjectPublicKeyInfo PEM, readable by any Ed25519 tool."""
    return load_public_key_hex(hex_key).public_bytes(
        _PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )


def load_pinned_public_key(path: str | Path) -> str:
    """Read the key a verifier should expect, as PEM or as 64 hex characters.

    Returns the raw key as hex, the form ``signed_root.json`` stores. Raises
    ``ValueError`` for anything that is not an Ed25519 public key, and ``OSError`` if
    the file cannot be read: a pin that silently failed to load would be no pin at all.
    """
    data = Path(path).read_bytes()
    if b"-----BEGIN" in data:
        key = serialization.load_pem_public_key(data)
        if not isinstance(key, Ed25519PublicKey):
            raise ValueError("pinned key must be an Ed25519 public key")
        return public_key_hex(key)
    text = data.decode("ascii", errors="replace").strip()
    return public_key_hex(load_public_key_hex(text))
