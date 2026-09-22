"""Ed25519 signing keys for the ledger.

Ed25519 (RFC 8032) because its signatures are *deterministic*: no nonce, so the
same key over the same root always yields the same bytes, and a committed example
ledger verifies identically forever. It also has no parameter choices to get
wrong, which is the failure mode that actually bites in ECDSA deployments.

The key path is config-driven; a KMS/HSM signer would replace this loader.
"""

from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_ledger_key() -> Ed25519PrivateKey:
    """Generate a fresh Ed25519 private key."""
    return Ed25519PrivateKey.generate()


def save_ledger_key(key: Ed25519PrivateKey, path: str | Path) -> Path:
    """Write ``key`` to ``path`` as unencrypted PKCS#8 PEM, owner-readable only."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    return destination


def load_ledger_key(path: str | Path) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from a PEM file."""
    data = Path(path).read_bytes()
    key = serialization.load_pem_private_key(data, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError(f"{path} is not an Ed25519 private key: {type(key).__name__}")
    return key


def public_key_hex(key: Ed25519PrivateKey | Ed25519PublicKey) -> str:
    """Return the hex-encoded raw 32-byte Ed25519 public key."""
    public = key.public_key() if isinstance(key, Ed25519PrivateKey) else key
    raw = public.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw.hex()


def public_key_from_hex(value: str) -> Ed25519PublicKey:
    """Rebuild an Ed25519 public key from its hex-encoded raw form."""
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"public key is not valid hex: {value!r}") from exc
    if len(raw) != 32:
        raise ValueError(f"Ed25519 public key must be 32 bytes, got {len(raw)}")
    return Ed25519PublicKey.from_public_bytes(raw)
