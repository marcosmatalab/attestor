"""ISO/IEC 42001:2023 crosswalk derived from a classification.

A REFERENCE crosswalk: for each AI Act obligation the classifier emitted, it points to
the related ISO/IEC 42001 management-system clauses (4-10) and Annex A control groups
(A.2-A.10). It is NOT an audit, certification, gap assessment, or statement of
conformity. Like the Annex IV obligation->section map (F3), the mapping is a defensible
design artifact, not something the standard prescribes.

Copyright: ISO/IEC 42001 is a paid standard. This module references only clause/control
IDENTIFIERS and the short group titles (headings) — it reproduces no normative text. The
Annex A numbering follows ISO/IEC 42001:2023 exactly (A.5 Assessing impacts, A.6 AI
system life cycle, A.7 Data, A.8 Information for interested parties, A.9 Use, A.10
Third-party), which several secondary sources get wrong.
"""

from pydantic import BaseModel, ConfigDict

from attestor.classifier.model import Classification, RiskTier

# ISO/IEC 42001:2023 management-system clauses (Harmonized Structure).
ISO_42001_CLAUSES: dict[str, str] = {
    "4": "Context of the organization",
    "5": "Leadership",
    "6": "Planning",
    "7": "Support",
    "8": "Operation",
    "9": "Performance evaluation",
    "10": "Improvement",
}

# ISO/IEC 42001:2023 Annex A control groups (38 controls across nine groups A.2-A.10).
ISO_42001_ANNEX_A: dict[str, str] = {
    "A.2": "Policies related to AI",
    "A.3": "Internal organization",
    "A.4": "Resources for AI systems",
    "A.5": "Assessing impacts of AI systems",
    "A.6": "AI system life cycle",
    "A.7": "Data for AI systems",
    "A.8": "Information for interested parties of AI systems",
    "A.9": "Use of AI systems",
    "A.10": "Third-party and customer relationships",
}

# Defensible obligation -> ISO/IEC 42001 mapping (clause ids and Annex A group ids).
# Curated subset: AI-Act-specific regulatory procedures with no clean 42001 analogue
# (Art. 5 prohibition; Arts 43/47/48/49 conformity, declaration, CE marking, registration)
# are deliberately omitted rather than mapped to a stretch.
OBLIGATION_ISO_MAP: dict[str, tuple[str, ...]] = {
    "art9_risk_management": ("6", "A.5", "A.6"),
    "art10_data_governance": ("A.7",),
    "art11_technical_documentation": ("7", "A.6"),
    "art12_record_keeping": ("9", "A.6"),
    "art13_transparency_deployers": ("A.8",),
    "art14_human_oversight": ("A.9", "A.6"),
    "art15_accuracy_robustness": ("8", "A.6"),
    "art16_provider_obligations": ("5", "A.2", "A.3"),
    "art17_quality_management": ("5", "A.2", "A.3"),
    "art26_6_log_retention": ("A.9",),
    "art27_fria": ("6", "A.5"),
    "art50_1_chatbot": ("A.8",),
    "art50_2_marking": ("A.8",),
    "art50_3_emotion_biometric": ("A.8",),
    "art50_4_deepfake": ("A.8",),
    "gpai_art53_documentation": ("7", "A.6"),
    "gpai_art55_systemic_risk": ("6", "A.5"),
}

_DISCLAIMER = (
    "Reference crosswalk only: it locates ISO/IEC 42001:2023 clauses and Annex A control "
    "groups related to each applied AI Act obligation. It is NOT an audit, certification, "
    "gap assessment, or statement of conformity with ISO/IEC 42001 or the AI Act. Only "
    "clause/control identifiers and group titles are cited; no normative text of the "
    "standard is reproduced (ISO/IEC 42001 is a paid standard)."
)


class Iso42001Reference(BaseModel):
    """One ISO/IEC 42001 clause or Annex A control group (identifier + heading)."""

    model_config = ConfigDict(frozen=True)

    kind: str  # "clause" | "annex_a"
    id: str  # e.g. "6" or "A.5"
    title: str  # the short group/clause heading (an identifier, not normative text)

    @property
    def label(self) -> str:
        return f"Clause {self.id}" if self.kind == "clause" else f"Annex {self.id}"


class CrosswalkEntry(BaseModel):
    """One applied AI Act obligation and the ISO/IEC 42001 areas related to it."""

    model_config = ConfigDict(frozen=True)

    obligation_id: str
    reference: str  # the AI Act article, e.g. "Art. 9"
    title: str
    iso_references: tuple[Iso42001Reference, ...]


class Iso42001Crosswalk(BaseModel):
    """A deterministic reference crosswalk derived from a classification."""

    model_config = ConfigDict(frozen=True)

    risk: RiskTier
    bundle_version: str
    classification_checksum: str
    entries: tuple[CrosswalkEntry, ...]
    disclaimer: str = _DISCLAIMER


def _reference(ref_id: str) -> Iso42001Reference:
    if ref_id in ISO_42001_CLAUSES:
        return Iso42001Reference(kind="clause", id=ref_id, title=ISO_42001_CLAUSES[ref_id])
    return Iso42001Reference(kind="annex_a", id=ref_id, title=ISO_42001_ANNEX_A[ref_id])


def derive_crosswalk(classification: Classification) -> Iso42001Crosswalk:
    """Build the ISO/IEC 42001 reference crosswalk for ``classification``'s obligations."""
    entries = tuple(
        CrosswalkEntry(
            obligation_id=obligation.id,
            reference=obligation.reference,
            title=obligation.title,
            iso_references=tuple(_reference(r) for r in OBLIGATION_ISO_MAP[obligation.id]),
        )
        for obligation in classification.obligations
        if obligation.id in OBLIGATION_ISO_MAP
    )
    return Iso42001Crosswalk(
        risk=classification.risk,
        bundle_version=classification.bundle_version,
        classification_checksum=classification.checksum,
        entries=entries,
    )
