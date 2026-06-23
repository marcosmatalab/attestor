"""Public artifact models for the ledger — what an offline verifier consumes.

All fields are public: hex hashes, a hex Ed25519 public key and signature, and (if
present) a base64 RFC 3161 token. None of these is secret; the private signing key
never appears. ``LedgerVerification`` keeps the tamper check (integrity + signature)
SEPARATE from TSA trust, the same way F5 separates C2PA integrity from signer trust.
"""

from pydantic import BaseModel, ConfigDict


class InclusionProof(BaseModel):
    """An RFC 6962 audit path proving one record is in the tree, without the tree."""

    model_config = ConfigDict(frozen=True)

    leaf_index: int
    tree_size: int
    leaf_hash: str  # hex
    audit_path: tuple[str, ...]  # hex sibling hashes, leaf -> root
    merkle_root: str  # hex


class TimestampInfo(BaseModel):
    """An RFC 3161 timestamp over the signed root's Ed25519 signature.

    ``token_b64`` is the authoritative artifact (the full DER response, base64). The
    other fields are informational, extracted from the token for display.
    """

    model_config = ConfigDict(frozen=True)

    token_b64: str
    tsa_name: str | None = None
    gen_time: str | None = None  # ISO 8601, informational


class SignedRoot(BaseModel):
    """The signed commitment over a sealed ledger: the public, verifiable artifact."""

    model_config = ConfigDict(frozen=True)

    merkle_root: str  # hex
    leaf_count: int
    algorithm: str = "ed25519"
    public_key: str  # hex, raw 32-byte Ed25519 public key
    signature: str  # hex, 64-byte Ed25519 signature over the root commitment
    timestamp: TimestampInfo | None = None


class LedgerVerification(BaseModel):
    """The result of an offline verification, with trust kept as a separate axis."""

    model_config = ConfigDict(frozen=True)

    # --- TAMPER CHECK: this, and only this, decides whether the ledger is intact ---
    integrity_ok: bool  # recomputed Merkle root matches the signed root
    signature_ok: bool  # Ed25519 signature valid over the root commitment
    # --- TIMESTAMP: a SEPARATE axis. A valid token from an unrecognised TSA does NOT
    #     make the ledger "tampered"; tsa_trusted is reported on its own (fail-closed). ---
    has_timestamp: bool = False
    timestamp_ok: bool = False  # token cryptographically valid AND bound to the signature
    tsa_trusted: bool = False  # TSA is a recognised authority (no list shipped -> False)
    gen_time: str | None = None
    detail: str = ""

    @property
    def verified(self) -> bool:
        """True iff the ledger is intact and signed. NOT gated on TSA trust."""
        return self.integrity_ok and self.signature_ok

    @property
    def headline(self) -> str:
        """One line that never conflates 'untrusted TSA' with 'tampered ledger'."""
        if not self.verified:
            return (
                "ledger TAMPERED - "
                f"integrity_ok={self.integrity_ok}, signature_ok={self.signature_ok}"
            )
        core = "ledger VERIFIED (Merkle root intact, Ed25519 signature valid)"
        if not self.has_timestamp:
            return f"{core}; no timestamp"
        if not self.timestamp_ok:
            return f"{core}; timestamp present but NOT verified ({self.detail})"
        trust = "TSA TRUSTED" if self.tsa_trusted else "TSA UNTRUSTED (not a recognised authority)"
        return f"{core}; timestamped {self.gen_time} - {trust}"
