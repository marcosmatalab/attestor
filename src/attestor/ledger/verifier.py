"""Offline verification of a ledger.

"Offline" is the whole point and it is literal: this module imports no network
client and needs no key material beyond the public key carried in the sealed
root. A third party who has the two JSON files can reach the same verdict as the
issuer, on a laptop with the wifi off.

The verdict is reported on separate axes rather than as one boolean, because the
axes fail for different reasons and mean different things:

- ``integrity_ok``  the Merkle root recomputed from the records matches the sealed
  one. False means the records were edited after sealing.
- ``signature_ok``  the Ed25519 signature over the sealed root verifies under the
  public key in the file. False means the root itself was rewritten (or the key
  does not match).
- ``timestamp_ok``  ``None`` when no RFC3161 token is attached; otherwise whether
  the token binds to this root. Binding is not trust — see ``ledger.timestamp``.
"""

from cryptography.exceptions import InvalidSignature

from attestor.ledger.keys import public_key_from_hex
from attestor.ledger.merkle import merkle_root_of
from attestor.ledger.model import LedgerRecord, LedgerVerification, SignedRoot
from attestor.ledger.timestamp import timestamp_binds

VERIFIED_HEADLINE = "ledger VERIFIED (Merkle root intact, Ed25519 signature valid)"
TAMPERED_HEADLINE = "ledger TAMPERED"


def verify_ledger(records: list[LedgerRecord], root: SignedRoot) -> LedgerVerification:
    """Verify ``records`` against their sealed ``root``, with no network and no secrets."""
    recomputed = merkle_root_of([r.canonical_bytes() for r in records])
    integrity_ok = recomputed == root.merkle_root and len(records) == root.leaf_count

    signature_ok = _signature_ok(root)

    timestamp_ok: bool | None = None
    if root.timestamp is not None:
        timestamp_ok = timestamp_binds(root, root.timestamp)

    return LedgerVerification(
        integrity_ok=integrity_ok,
        signature_ok=signature_ok,
        timestamp_ok=timestamp_ok,
        leaf_count=len(records),
        merkle_root=root.merkle_root,
        recomputed_root=recomputed,
        detail=_detail(integrity_ok, signature_ok, timestamp_ok),
    )


def _signature_ok(root: SignedRoot) -> bool:
    try:
        public_key = public_key_from_hex(root.public_key)
        public_key.verify(bytes.fromhex(root.signature), root.signed_payload())
    except (InvalidSignature, ValueError):
        return False
    return True


def _timestamp_phrase(timestamp_ok: bool | None) -> str:
    if timestamp_ok is None:
        return "no timestamp"
    if timestamp_ok:
        return "RFC3161 token bound to this root (binding only, not TSA trust)"
    return "RFC3161 token does NOT bind to this root"


def _detail(integrity_ok: bool, signature_ok: bool, timestamp_ok: bool | None) -> str:
    if integrity_ok and signature_ok and timestamp_ok is not False:
        return f"{VERIFIED_HEADLINE}; {_timestamp_phrase(timestamp_ok)}"
    return (
        f"{TAMPERED_HEADLINE} - integrity_ok={integrity_ok}, "
        f"signature_ok={signature_ok}; {_timestamp_phrase(timestamp_ok)}"
    )
