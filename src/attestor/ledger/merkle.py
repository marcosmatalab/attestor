"""Deterministic Merkle tree over ledger leaves (RFC 6962).

RFC 6962's Merkle Tree Hash with domain separation — a ``0x00`` prefix for leaves and a
``0x01`` prefix for internal nodes — so a leaf hash can never be reinterpreted as an
internal node (second-preimage resistance). Unlike Bitcoin-style trees, an odd node is
carried up unchanged rather than duplicated, which removes the duplicate-leaf ambiguity.
The construction is fully deterministic: the same ordered leaves always yield the same
root, and an inclusion proof lets a third party verify membership with only the audit
path — never the whole tree.
"""

import hashlib

_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"


def hash_leaf(entry: bytes) -> bytes:
    """RFC 6962 leaf hash: ``SHA-256(0x00 || entry)``."""
    return hashlib.sha256(_LEAF_PREFIX + entry).digest()


def _hash_node(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def _split(n: int) -> int:
    """Largest power of two strictly less than ``n`` (RFC 6962 split point, n >= 2)."""
    k = 1
    while k << 1 < n:
        k <<= 1
    return k


def merkle_root(leaves: list[bytes]) -> bytes:
    """RFC 6962 Merkle Tree Hash over the already-hashed ``leaves`` (>= 1)."""
    if not leaves:
        raise ValueError("Merkle tree requires at least one leaf")
    if len(leaves) == 1:
        return leaves[0]
    k = _split(len(leaves))
    return _hash_node(merkle_root(leaves[:k]), merkle_root(leaves[k:]))


def inclusion_proof(leaves: list[bytes], index: int) -> list[bytes]:
    """RFC 6962 audit path for ``index``: sibling hashes from the leaf up to the root."""
    n = len(leaves)
    if not 0 <= index < n:
        raise IndexError(f"leaf index {index} out of range for {n} leaves")
    if n == 1:
        return []
    k = _split(n)
    if index < k:
        return [*inclusion_proof(leaves[:k], index), merkle_root(leaves[k:])]
    return [*inclusion_proof(leaves[k:], index - k), merkle_root(leaves[:k])]


def verify_inclusion(
    leaf_hash: bytes, index: int, tree_size: int, audit_path: list[bytes], root: bytes
) -> bool:
    """Verify ``leaf_hash`` is the ``index``-th of ``tree_size`` leaves under ``root``.

    Implements RFC 6962 §2.1.1: a third party needs only the leaf, its index, the tree
    size, the audit path, and the root — never the other leaves or the whole tree.
    """
    if not 0 <= index < tree_size:
        return False
    node, last = index, tree_size - 1
    computed = leaf_hash
    for sibling in audit_path:
        if last == 0:
            return False  # audit path longer than the tree allows
        if (node & 1) or (node == last):
            computed = _hash_node(sibling, computed)
            while node and not (node & 1):
                node >>= 1
                last >>= 1
        else:
            computed = _hash_node(computed, sibling)
        node >>= 1
        last >>= 1
    return last == 0 and computed == root
