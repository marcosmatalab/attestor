"""Domain model for the governance layer (F7).

Everything here is *derived* from a ``Classification``, like the Annex IV dossier:
the governance views never decide what applies, they re-present what the
deterministic classifier already decided, in the shape an auditor or a management
system asks for.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict


class ControlMapping(BaseModel):
    """One AI Act obligation mapped onto an ISO/IEC 42001 anchor."""

    model_config = ConfigDict(frozen=True)

    obligation_id: str
    reference: str  # e.g. "Art. 9"
    title: str
    effective_date: date
    iso_clause: str  # e.g. "6.1" or "A.5.2"
    iso_title: str
    rationale: str


class ManagementSystemMap(BaseModel):
    """The full AI Act -> ISO/IEC 42001 view for one classification."""

    model_config = ConfigDict(frozen=True)

    bundle_version: str
    bundle_sha256: str
    classification_checksum: str
    mappings: tuple[ControlMapping, ...]
    unmapped_obligations: tuple[str, ...]

    @property
    def clauses(self) -> tuple[str, ...]:
        """Every distinct ISO clause touched, in stable order."""
        return tuple(sorted({m.iso_clause for m in self.mappings}))


class FriaElement(BaseModel):
    """One of the elements Art. 27(1) requires a FRIA to describe."""

    model_config = ConfigDict(frozen=True)

    point: str  # "a".."f"
    title: str
    guidance: str


class FriaAssessment(BaseModel):
    """Art. 27 applicability plus, when it applies, the scaffold to complete."""

    model_config = ConfigDict(frozen=True)

    required: bool
    reason: str
    effective_date: date | None
    elements: tuple[FriaElement, ...]


class LogRetentionDuty(BaseModel):
    """A record-keeping duty with the retention floor the Regulation sets."""

    model_config = ConfigDict(frozen=True)

    obligation_id: str
    reference: str
    title: str
    effective_date: date
    minimum_retention_months: int
    note: str
