"""Cryptographic ledger: append-only records, Merkle root, Ed25519 + RFC3161.

An append-only log whose records are committed into a deterministic RFC 6962 Merkle
tree; the root is signed with Ed25519 and optionally timestamped (RFC 3161). A third
party verifies integrity, signature, and (if present) the timestamp **offline** — with
only public artifacts, no private key and no network. This is integrity-and-existence
evidence, NOT a blockchain (no distribution, no consensus); see the README honesty note.
"""

from attestor.ledger.keys import (
    LedgerKeyConfig,
    generate_ledger_key,
    load_private_key,
    load_public_key_hex,
    public_key_hex,
)

__all__ = [
    "LedgerKeyConfig",
    "generate_ledger_key",
    "load_private_key",
    "load_public_key_hex",
    "public_key_hex",
]
