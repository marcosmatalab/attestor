"""Verification report model: integrity and signer trust as SEPARATE dimensions.

A C2PA verification answers two independent questions that must never be conflated:

* **Integrity** — is the manifest intact and the claim well-formed? (``validation_state``)
* **Trust** — is the *signer* recognised by a trust list? (``trusted`` / ``trust_reason``)

"Valid" integrity does NOT imply a trusted signer. The report keeps the two apart and,
via :pyattr:`VerificationReport.headline`, never states integrity without the trust
qualifier. The model is pure data (no c2pa import); :mod:`attestor.provenance.verifier`
populates it.
"""

from pydantic import BaseModel, ConfigDict


class SignerIdentity(BaseModel):
    """Who signed: identity fields from the leaf certificate. NOT a trust claim."""

    model_config = ConfigDict(frozen=True)

    common_name: str | None = None
    issuer: str | None = None
    cert_serial_number: str | None = None
    algorithm: str | None = None


class AiDisclosure(BaseModel):
    """The AI-generation signal carried by the manifest's assertions, if any.

    ``digital_source_type`` is the portable IPTC signal any C2PA reader sees;
    ``ai_generated`` / ``eu_ai_act_art50`` come from Attestor's custom assertion.
    Absence of a disclosure does NOT imply the content is non-AI (it is voluntary).
    """

    model_config = ConfigDict(frozen=True)

    ai_generated: bool | None = None
    digital_source_type: str | None = None
    eu_ai_act_art50: bool | None = None
    labels: tuple[str, ...] = ()


class ValidationCodes(BaseModel):
    """Raw C2PA validation-result codes for auditability.

    Only the ``code`` strings are kept — never the ``url`` fields, which embed a
    per-signature random URN that would make the report non-deterministic.
    """

    model_config = ConfigDict(frozen=True)

    success: tuple[str, ...] = ()
    informational: tuple[str, ...] = ()
    failure: tuple[str, ...] = ()


class VerificationReport(BaseModel):
    """Deterministic verification report separating integrity from signer trust."""

    model_config = ConfigDict(frozen=True)

    has_manifest: bool
    # --- INTEGRITY: manifest intact + claim well-formed ---
    validation_state: str | None = None
    integrity_ok: bool = False
    # --- TRUST: is the signer recognised? Reported SEPARATELY; fail-closed. ---
    trusted: bool = False
    trust_reason: str = ""
    # --- detail ---
    signer: SignerIdentity | None = None
    ai_disclosure: AiDisclosure | None = None
    validation_codes: ValidationCodes | None = None

    @property
    def headline(self) -> str:
        """One line that NEVER reports integrity without the trust qualifier."""
        if not self.has_manifest:
            return "no C2PA manifest found"
        integrity = (
            f"integrity {self.validation_state} (manifest intact, claim well-formed)"
            if self.integrity_ok
            else f"integrity {self.validation_state} (FAILED)"
        )
        trust = "signer TRUSTED" if self.trusted else f"signer UNTRUSTED — {self.trust_reason}"
        return f"{integrity}; {trust}"
