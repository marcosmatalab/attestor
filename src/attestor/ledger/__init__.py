"""Cryptographic ledger: Ed25519 + Merkle (RFC 6962) + RFC3161, verifiable offline.

The ledger anchors what the rest of the engine produced — a classification, an
Annex IV dossier, a C2PA manifest — by digest, never by value. Its promise is
narrow and therefore keepable: *these artifacts existed in exactly this form, in
this order, before this root was sealed*.

Verification needs no network, no secrets and no clone of this repo: the two JSON
files plus the public key inside them are enough. ``examples/ledger`` is a
committed, verifiable instance of exactly that.
"""

from attestor.ledger.keys import (
    generate_ledger_key,
    ledger_key_from_settings,
    load_ledger_key,
    public_key_from_hex,
    public_key_hex,
    save_ledger_key,
)
from attestor.ledger.ledger import (
    Ledger,
    LedgerError,
    attach_timestamp,
    load_ledger,
    save_ledger,
)
from attestor.ledger.merkle import merkle_root, merkle_root_of
from attestor.ledger.model import (
    LedgerRecord,
    LedgerVerification,
    RecordTimestamp,
    SignedRoot,
)
from attestor.ledger.timestamp import (
    TimestampError,
    build_timestamp_request,
    parse_timestamp,
    root_digest,
    timestamp_binds,
)
from attestor.ledger.verifier import verify_ledger

__all__ = [
    "Ledger",
    "LedgerError",
    "LedgerRecord",
    "LedgerVerification",
    "RecordTimestamp",
    "SignedRoot",
    "TimestampError",
    "attach_timestamp",
    "build_timestamp_request",
    "generate_ledger_key",
    "ledger_key_from_settings",
    "load_ledger",
    "load_ledger_key",
    "merkle_root",
    "merkle_root_of",
    "parse_timestamp",
    "public_key_from_hex",
    "public_key_hex",
    "root_digest",
    "save_ledger",
    "save_ledger_key",
    "timestamp_binds",
    "verify_ledger",
]
