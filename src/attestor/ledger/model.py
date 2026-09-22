"""Domain model for the cryptographic ledger.

A ledger is an append-only list of ``LedgerRecord`` entries plus a ``SignedRoot``
that seals them. The split matters for verification: the signature covers the
*root*, not the records, so the two failure modes stay distinguishable — an
altered record breaks ``integrity_ok`` while ``signature_ok`` stays true, which
tells an auditor "someone edited the evidence", not "the key is wrong".
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from attestor.canonical import canonical_json

LEDGER_ALGORITHM = "ed25519"


class RecordTimestamp(BaseModel):
    """An RFC3161 token bound to a signed root (see ``ledger.timestamp``)."""

    model_config = ConfigDict(frozen=True)

    tsr_sha256: str
    gen_time: datetime
    message_imprint: str  # hex digest the TSA attested to
    policy: str | None = None


class LedgerRecord(BaseModel):
    """One anchored artifact: what it was, what it was about, and its digest.

    The record never carries the artifact itself — only its SHA-256. The ledger is
    evidence *that* something existed in a given form at a given position, not a
    store of the thing.
    """

    model_config = ConfigDict(frozen=True)

    id: str
    kind: str  # "classification" | "annex-iv-dossier" | "c2pa-manifest" | ...
    subject: str  # the AI system this record is about
    payload_sha256: str
    recorded_at: datetime

    def canonical_bytes(self) -> bytes:
        """The exact bytes hashed into the Merkle leaf."""
        return canonical_json(self.model_dump(mode="json"))


class SignedRoot(BaseModel):
    """The Ed25519-signed Merkle root that seals a ledger."""

    model_config = ConfigDict(frozen=True)

    merkle_root: str
    leaf_count: int
    algorithm: str = LEDGER_ALGORITHM
    public_key: str  # hex-encoded Ed25519 public key (32 bytes)
    signature: str  # hex-encoded Ed25519 signature over ``signed_payload``
    sealed_at: datetime
    timestamp: RecordTimestamp | None = None

    def signed_payload(self) -> bytes:
        """The canonical bytes the Ed25519 signature is computed over.

        Deliberately excludes ``signature`` and ``timestamp``: the signature cannot
        cover itself, and the RFC3161 token is attached *after* sealing (it
        timestamps the root, so it cannot be an input to it).
        """
        return canonical_json(
            {
                "algorithm": self.algorithm,
                "leaf_count": self.leaf_count,
                "merkle_root": self.merkle_root,
                "public_key": self.public_key,
                "sealed_at": self.sealed_at.isoformat().replace("+00:00", "Z"),
            }
        )


class LedgerVerification(BaseModel):
    """The result of verifying a ledger offline. Two independent axes."""

    model_config = ConfigDict(frozen=True)

    integrity_ok: bool  # recomputed Merkle root matches the sealed one
    signature_ok: bool  # Ed25519 signature over the sealed root verifies
    timestamp_ok: bool | None  # None when no RFC3161 token is attached
    leaf_count: int
    merkle_root: str
    recomputed_root: str
    detail: str

    @property
    def verified(self) -> bool:
        """True only when every applicable axis holds."""
        return self.integrity_ok and self.signature_ok and self.timestamp_ok is not False
