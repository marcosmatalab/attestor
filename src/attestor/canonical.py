"""Deterministic canonical JSON serialization and hashing.

Shared low-level primitive. The classifier (F1) uses it for content-addressed,
reproducible checksums; the cryptographic ledger (F6) will reuse it for Merkle
leaves. The canonical form is the contract that makes "same input -> same output"
auditable across machines and time:

- keys sorted (order-independent),
- no insignificant whitespace,
- UTF-8 (non-ASCII preserved, not escaped),
- NaN / Infinity rejected (not valid JSON, and not reproducible).
"""

import hashlib
import json
from typing import Any


def canonical_json(obj: Any) -> bytes:
    """Serialize ``obj`` to canonical, deterministic JSON bytes."""
    return json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Return the hex-encoded SHA-256 digest of ``data``."""
    return hashlib.sha256(data).hexdigest()
