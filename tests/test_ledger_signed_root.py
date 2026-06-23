"""Tests for sealing an append-only ledger into a signed Merkle root."""

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.ledger import (
    Ledger,
    SignedRoot,
    load_ledger,
    load_public_key_hex,
    prove_inclusion,
    root_commitment,
    save_ledger,
    seal,
)

# A fixed test key (deterministic seed) — a throwaway, NEVER a real secret.
_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
_RECORDS = [
    {"type": "dossier", "id": "sys-1", "sha256": "aa"},
    {"type": "c2pa", "id": "img-1", "sha256": "bb"},
    {"type": "dossier", "id": "sys-2", "sha256": "cc"},
]


def test_seal_is_deterministic() -> None:
    # Same records + same key -> identical root AND identical signature (RFC 8032).
    first = seal(_RECORDS, _TEST_KEY)
    second = seal(_RECORDS, _TEST_KEY)
    assert first == second
    assert len(bytes.fromhex(first.signature)) == 64
    assert first.leaf_count == 3
    assert first.algorithm == "ed25519"


def test_signature_verifies_over_the_root_commitment() -> None:
    signed = seal(_RECORDS, _TEST_KEY)
    public_key = load_public_key_hex(signed.public_key)
    # The signature covers canonical(merkle_root + leaf_count).
    public_key.verify(
        bytes.fromhex(signed.signature),
        root_commitment(signed.merkle_root, signed.leaf_count),
    )


def test_record_order_changes_the_root() -> None:
    # Append-only ordering is meaningful: reordering yields a different commitment.
    reordered = [_RECORDS[2], _RECORDS[1], _RECORDS[0]]
    assert seal(_RECORDS, _TEST_KEY).merkle_root != seal(reordered, _TEST_KEY).merkle_root


def test_empty_ledger_cannot_be_sealed() -> None:
    with pytest.raises(ValueError, match="empty ledger"):
        seal([], _TEST_KEY)


def test_ledger_append_is_ordered() -> None:
    ledger = Ledger()
    assert ledger.append({"a": 1}) == 0
    assert ledger.append({"b": 2}) == 1
    assert ledger.records == [{"a": 1}, {"b": 2}]
    # Sealing the class matches the functional form.
    assert ledger.seal(_TEST_KEY) == seal([{"a": 1}, {"b": 2}], _TEST_KEY)


def test_inclusion_proof_matches_sealed_root() -> None:
    signed = seal(_RECORDS, _TEST_KEY)
    proof = prove_inclusion(_RECORDS, 1)
    assert proof.merkle_root == signed.merkle_root
    assert proof.tree_size == 3
    assert proof.leaf_index == 1


def test_save_and_load_roundtrips(tmp_path: Path) -> None:
    signed = seal(_RECORDS, _TEST_KEY)
    save_ledger(tmp_path, _RECORDS, signed)

    records, loaded = load_ledger(tmp_path)
    assert records == _RECORDS  # order preserved
    assert isinstance(loaded, SignedRoot)
    assert loaded == signed  # round-trips through JSON unchanged
    assert (tmp_path / "records.json").is_file()
    assert (tmp_path / "signed_root.json").is_file()
