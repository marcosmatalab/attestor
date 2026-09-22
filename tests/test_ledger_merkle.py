"""Merkle tree behaviour that the tamper-evidence claim depends on."""

import hashlib

import pytest

from attestor.ledger.merkle import (
    EMPTY_ROOT,
    leaf_hash,
    merkle_root,
    merkle_root_of,
    node_hash,
)


def test_empty_tree_is_the_hash_of_the_empty_string() -> None:
    assert merkle_root([]) == EMPTY_ROOT == hashlib.sha256(b"").hexdigest()


def test_single_leaf_root_is_the_leaf_hash() -> None:
    assert merkle_root_of([b"a"]) == leaf_hash(b"a").hex()


def test_leaf_and_node_prefixes_are_domain_separated() -> None:
    # Without the RFC 6962 prefixes these two would collide, which is exactly the
    # second-preimage attack the prefixes exist to prevent.
    assert leaf_hash(b"x") != hashlib.sha256(b"x").digest()
    assert node_hash(b"l" * 32, b"r" * 32) != hashlib.sha256(b"l" * 32 + b"r" * 32).digest()


def test_root_changes_when_any_leaf_changes() -> None:
    assert merkle_root_of([b"a", b"b", b"c"]) != merkle_root_of([b"a", b"b", b"d"])


def test_root_changes_when_leaf_order_changes() -> None:
    assert merkle_root_of([b"a", b"b"]) != merkle_root_of([b"b", b"a"])


def test_odd_node_is_promoted_not_duplicated() -> None:
    # CVE-2012-2459: duplicating the last node makes [a, b, c] and [a, b, c, c]
    # collide. RFC 6962 promotes instead, so they must differ.
    assert merkle_root_of([b"a", b"b", b"c"]) != merkle_root_of([b"a", b"b", b"c", b"c"])


@pytest.mark.parametrize("count", [1, 2, 3, 4, 5, 8, 9, 17])
def test_root_is_stable_across_runs(count: int) -> None:
    payloads = [f"leaf-{i}".encode() for i in range(count)]
    assert merkle_root_of(payloads) == merkle_root_of(payloads)
