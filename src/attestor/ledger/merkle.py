"""Merkle tree over ledger records, following RFC 6962 (Certificate Transparency).

RFC 6962 rather than a naive tree because the domain-separation prefixes are what
make the structure sound: a leaf is hashed as ``SHA-256(0x00 || data)`` and an
internal node as ``SHA-256(0x01 || left || right)``. Without those prefixes an
attacker can present an internal node as if it were a leaf (second-preimage), and
"the ledger is tamper-evident" stops being true.

Odd nodes are promoted unchanged to the next level (RFC 6962 does not duplicate
the last node, which is the CVE-2012-2459 bug in Bitcoin's variant).
"""

import hashlib

_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"

# RFC 6962 s2.1: the hash of the empty tree is the hash of the empty string.
EMPTY_ROOT = hashlib.sha256(b"").hexdigest()


def leaf_hash(data: bytes) -> bytes:
    """Return the RFC 6962 leaf hash of ``data``."""
    return hashlib.sha256(_LEAF_PREFIX + data).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    """Return the RFC 6962 internal-node hash of two child hashes."""
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def merkle_root(leaves: list[bytes]) -> str:
    """Return the hex Merkle root over already-hashed ``leaves``."""
    if not leaves:
        return EMPTY_ROOT

    level = list(leaves)
    while len(level) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(node_hash(level[i], level[i + 1]))
        if len(level) % 2 == 1:
            # Promote the odd node unchanged; never duplicate it.
            nxt.append(level[-1])
        level = nxt
    return level[0].hex()


def merkle_root_of(payloads: list[bytes]) -> str:
    """Return the hex Merkle root over raw (unhashed) leaf payloads."""
    return merkle_root([leaf_hash(p) for p in payloads])
