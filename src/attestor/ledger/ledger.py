"""Append-only ledger: hash records into a Merkle tree, sign the root with Ed25519.

Records are appended in order and never reordered or removed. Each leaf is the RFC 6962
hash of the record's canonical JSON (reusing :mod:`attestor.canonical`, the same
serialization the classifier checksums with), so the verifier recomputes identical leaf
hashes. ``seal`` produces the Merkle root and an Ed25519 signature over the root
commitment — a deterministic, publishable :class:`SignedRoot`.
"""

import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.canonical import canonical_json
from attestor.ledger.keys import public_key_hex
from attestor.ledger.merkle import hash_leaf, inclusion_proof, merkle_root
from attestor.ledger.model import InclusionProof, SignedRoot

Record = dict[str, Any]


def root_commitment(merkle_root_hex: str, leaf_count: int) -> bytes:
    """Canonical bytes the Ed25519 signature covers (binds the root to the leaf count)."""
    return canonical_json({"leaf_count": leaf_count, "merkle_root": merkle_root_hex})


def _leaves(records: list[Record]) -> list[bytes]:
    return [hash_leaf(canonical_json(record)) for record in records]


def seal(records: list[Record], private_key: Ed25519PrivateKey) -> SignedRoot:
    """Compute the Merkle root over ``records`` and sign it with Ed25519 (deterministic)."""
    if not records:
        raise ValueError("cannot seal an empty ledger")
    root_hex = merkle_root(_leaves(records)).hex()
    signature = private_key.sign(root_commitment(root_hex, len(records)))
    return SignedRoot(
        merkle_root=root_hex,
        leaf_count=len(records),
        public_key=public_key_hex(private_key.public_key()),
        signature=signature.hex(),
    )


def prove_inclusion(records: list[Record], index: int) -> InclusionProof:
    """Build an RFC 6962 inclusion proof for ``records[index]``."""
    leaves = _leaves(records)
    return InclusionProof(
        leaf_index=index,
        tree_size=len(records),
        leaf_hash=leaves[index].hex(),
        audit_path=tuple(h.hex() for h in inclusion_proof(leaves, index)),
        merkle_root=merkle_root(leaves).hex(),
    )


class Ledger:
    """An append-only sequence of records, sealable into a signed Merkle root."""

    def __init__(self, records: list[Record] | None = None) -> None:
        self._records: list[Record] = list(records) if records else []

    def append(self, record: Record) -> int:
        """Append a record and return its leaf index. Append-only: never reorders."""
        self._records.append(record)
        return len(self._records) - 1

    @property
    def records(self) -> list[Record]:
        return list(self._records)

    def seal(self, private_key: Ed25519PrivateKey) -> SignedRoot:
        return seal(self._records, private_key)

    def prove_inclusion(self, index: int) -> InclusionProof:
        return prove_inclusion(self._records, index)


def save_ledger(directory: str | Path, records: list[Record], signed_root: SignedRoot) -> None:
    """Write the public artifacts (records + signed root) for offline verification."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    (target / "records.json").write_bytes(canonical_json(records))
    (target / "signed_root.json").write_bytes(
        canonical_json(signed_root.model_dump(exclude_none=True))
    )


def load_ledger(directory: str | Path) -> tuple[list[Record], SignedRoot]:
    """Load the public artifacts written by :func:`save_ledger` (records keep their order)."""
    source = Path(directory)
    records = json.loads((source / "records.json").read_bytes())
    signed_root = SignedRoot.model_validate_json((source / "signed_root.json").read_bytes())
    return records, signed_root
