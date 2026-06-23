"""Tests for the deterministic RFC 6962 Merkle tree."""

import hashlib

import pytest

from attestor.ledger.merkle import hash_leaf, inclusion_proof, merkle_root, verify_inclusion


def _leaves(n: int) -> list[bytes]:
    return [hash_leaf(f"record-{i}".encode()) for i in range(n)]


def _node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(b"\x01" + left + right).digest()


def test_leaf_hash_is_domain_separated() -> None:
    # Leaf prefix 0x00 — a leaf hash is never a bare SHA-256 of the content.
    assert hash_leaf(b"x") == hashlib.sha256(b"\x00x").digest()
    assert hash_leaf(b"x") != hashlib.sha256(b"x").digest()


def test_single_leaf_root_is_the_leaf() -> None:
    leaves = _leaves(1)
    assert merkle_root(leaves) == leaves[0]


def test_two_leaf_root_structure() -> None:
    leaves = _leaves(2)
    assert merkle_root(leaves) == _node(leaves[0], leaves[1])


def test_three_leaf_root_is_rfc6962_split() -> None:
    # n=3 -> k=2: HASH(node(l0,l1), l2), the odd leaf carried up (not duplicated).
    leaves = _leaves(3)
    expected = _node(_node(leaves[0], leaves[1]), leaves[2])
    assert merkle_root(leaves) == expected


def test_root_is_deterministic() -> None:
    assert merkle_root(_leaves(5)) == merkle_root(_leaves(5))


def test_empty_tree_rejected() -> None:
    with pytest.raises(ValueError, match="at least one leaf"):
        merkle_root([])


@pytest.mark.parametrize("size", [1, 2, 3, 4, 5, 7, 8, 16])
def test_inclusion_proof_verifies_for_every_leaf(size: int) -> None:
    leaves = _leaves(size)
    root = merkle_root(leaves)
    for index in range(size):
        path = inclusion_proof(leaves, index)
        assert verify_inclusion(leaves[index], index, size, path, root)


def test_inclusion_proof_rejects_tampered_leaf() -> None:
    leaves = _leaves(6)
    root = merkle_root(leaves)
    path = inclusion_proof(leaves, 3)

    forged = hash_leaf(b"not-the-record")
    assert not verify_inclusion(forged, 3, 6, path, root)


def test_inclusion_proof_rejects_wrong_index() -> None:
    leaves = _leaves(6)
    root = merkle_root(leaves)
    path = inclusion_proof(leaves, 3)

    # Same leaf and path but claimed at a different position -> rejected.
    assert not verify_inclusion(leaves[3], 2, 6, path, root)


def test_inclusion_proof_rejects_wrong_root() -> None:
    leaves = _leaves(6)
    path = inclusion_proof(leaves, 3)
    assert not verify_inclusion(leaves[3], 3, 6, path, hash_leaf(b"wrong-root"))


def test_inclusion_index_out_of_range() -> None:
    with pytest.raises(IndexError):
        inclusion_proof(_leaves(4), 4)
