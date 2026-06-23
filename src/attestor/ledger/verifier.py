"""Offline ledger verifier — public inputs only, no private key, no network.

:func:`verify_ledger` recomputes the Merkle root from the records (the SAME canonical
leaf hashing used when sealing), verifies the Ed25519 signature over the root
commitment, and — if a timestamp and TSA certificates are present — verifies the token
offline. The tamper check is integrity AND signature only; TSA trust is a separate axis
that NEVER decides whether the ledger was tampered (the F5 integrity-vs-trust lesson).
"""

import base64

from cryptography import x509
from cryptography.exceptions import InvalidSignature

from attestor.canonical import canonical_json
from attestor.ledger.keys import load_public_key_hex
from attestor.ledger.ledger import Record, root_commitment
from attestor.ledger.merkle import hash_leaf, merkle_root, verify_inclusion
from attestor.ledger.model import InclusionProof, LedgerVerification, SignedRoot
from attestor.ledger.timestamp import verify_timestamp


def verify_ledger(
    records: list[Record],
    signed_root: SignedRoot,
    *,
    tsa_leaf: x509.Certificate | None = None,
    tsa_root: x509.Certificate | None = None,
) -> LedgerVerification:
    """Verify a ledger from public artifacts alone (no private key, no network)."""
    integrity_ok = _verify_integrity(records, signed_root)
    signature_ok = _verify_signature(signed_root)

    has_timestamp = signed_root.timestamp is not None
    timestamp_ok = False
    tsa_trusted = False
    gen_time = signed_root.timestamp.gen_time if has_timestamp else None
    detail = ""
    if has_timestamp:
        if tsa_leaf is not None and tsa_root is not None:
            token = base64.b64decode(signed_root.timestamp.token_b64)
            message = bytes.fromhex(signed_root.signature)
            timestamp_ok, gen_time = verify_timestamp(
                token, message, tsa_leaf=tsa_leaf, tsa_root=tsa_root
            )
            # Fail-closed: no recognised-authority trust list ships, so a dev/free TSA
            # is reported untrusted even when its token is cryptographically valid.
            tsa_trusted = False
            if not timestamp_ok:
                detail = "token did not verify against the supplied TSA certificates"
        else:
            detail = "timestamp present but no TSA certificates supplied to verify it"

    return LedgerVerification(
        integrity_ok=integrity_ok,
        signature_ok=signature_ok,
        has_timestamp=has_timestamp,
        timestamp_ok=timestamp_ok,
        tsa_trusted=tsa_trusted,
        gen_time=gen_time,
        detail=detail,
    )


def verify_inclusion_proof(proof: InclusionProof, *, record: Record | None = None) -> bool:
    """Verify an inclusion proof against its root; if ``record`` is given, bind it too."""
    leaf = bytes.fromhex(proof.leaf_hash)
    if record is not None and hash_leaf(canonical_json(record)) != leaf:
        return False
    audit_path = [bytes.fromhex(h) for h in proof.audit_path]
    return verify_inclusion(
        leaf, proof.leaf_index, proof.tree_size, audit_path, bytes.fromhex(proof.merkle_root)
    )


def _verify_integrity(records: list[Record], signed_root: SignedRoot) -> bool:
    if len(records) != signed_root.leaf_count:
        return False
    try:
        recomputed = merkle_root([hash_leaf(canonical_json(r)) for r in records]).hex()
    except ValueError:
        return False
    return recomputed == signed_root.merkle_root


def _verify_signature(signed_root: SignedRoot) -> bool:
    try:
        public_key = load_public_key_hex(signed_root.public_key)
        public_key.verify(
            bytes.fromhex(signed_root.signature),
            root_commitment(signed_root.merkle_root, signed_root.leaf_count),
        )
    except (InvalidSignature, ValueError):
        return False
    return True
