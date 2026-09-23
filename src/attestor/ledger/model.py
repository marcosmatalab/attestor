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
    # --- SIGNER: whose key made the signature. The signature is checked with the key
    #     stored in signed_root.json, so on its own it proves consistency, not identity:
    #     anyone who re-seals edited records with a fresh key gets a valid signature.
    #     Pinning the expected key is what turns "a valid signature" into "HIS signature". ---
    signer_fingerprint: str = ""  # SHA-256 of the raw signing key, always reported
    signer_pinned: bool = False  # the caller named the key it expects
    signer_matches_pin: bool = False  # ...and the ledger was signed by exactly that key
    # Without a pin, "intact and signed" says nothing about WHO signed, so it is not a
    # pass unless the caller explicitly accepts that (``allow_unpinned``).
    unpinned_allowed: bool = False

    @property
    def tampered(self) -> bool:
        """The records or the signed root do not hold together. Always the worst verdict."""
        return not (self.integrity_ok and self.signature_ok)

    @property
    def untrusted_signer(self) -> bool:
        """Internally consistent, but sealed by a key other than the pinned one."""
        return not self.tampered and self.signer_pinned and not self.signer_matches_pin

    @property
    def signer_not_pinned(self) -> bool:
        """Intact and signed, but no key was pinned and the caller did not accept that."""
        return not self.tampered and not self.signer_pinned and not self.unpinned_allowed

    @property
    def verified(self) -> bool:
        """Intact, signed, and signed by the pinned key - or unpinned by explicit consent.

        NOT gated on TSA trust. Precedence: tampered, then untrusted signer, then signer
        not pinned; only a ledger clear of all three is verified.
        """
        return not (self.tampered or self.untrusted_signer or self.signer_not_pinned)

    @property
    def headline(self) -> str:
        """One line that never conflates 'untrusted TSA' with 'tampered ledger'."""
        if self.tampered:
            return (
                "ledger TAMPERED - "
                f"integrity_ok={self.integrity_ok}, signature_ok={self.signature_ok}"
            )
        if self.untrusted_signer:
            return (
                "ledger UNTRUSTED SIGNER - records intact and signed, "
                "but by a key other than the pinned one"
            )
        if self.signer_not_pinned:
            return (
                "ledger SIGNER NOT PINNED - records intact and signed, but no key was pinned: "
                "pass --public-key, or --allow-unpinned to accept any signer"
            )
        signer = (
            "signer pinned"
            if self.signer_pinned
            else "signer not pinned: compare signer_sha256 with the published key"
        )
        core = f"ledger VERIFIED (Merkle root intact, Ed25519 signature valid; {signer})"
        if not self.has_timestamp:
            return f"{core}; no timestamp"
        if not self.timestamp_ok:
            return f"{core}; timestamp present but NOT verified ({self.detail})"
        trust = "TSA TRUSTED" if self.tsa_trusted else "TSA UNTRUSTED (not a recognised authority)"
        return f"{core}; timestamped {self.gen_time} - {trust}"
