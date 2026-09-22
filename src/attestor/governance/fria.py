"""Fundamental rights impact assessment (Art. 27).

Applicability is **not** recomputed here. Art. 27 is already an obligation the
classifier emits from its bundle rules, so this module reads the classification
rather than re-deciding it: one source of truth, and the FRIA's effective date
comes from the same per-obligation date everything else uses.

What this module adds is the scaffold — the six elements Art. 27(1)(a)-(f) require
a FRIA to describe. Like the Annex IV dossier, it tells you what to write; it does
not write it.
"""

from attestor.classifier.model import Classification
from attestor.governance.model import FriaAssessment, FriaElement

FRIA_OBLIGATION_ID = "art27_fria"

# Art. 27(1)(a)-(f), Reg. (EU) 2024/1689.
FRIA_ELEMENTS: tuple[FriaElement, ...] = (
    FriaElement(
        point="a",
        title="Description of the deployer's processes",
        guidance="Describe the processes in which the high-risk AI system will be used, "
        "in line with its intended purpose.",
    ),
    FriaElement(
        point="b",
        title="Period and frequency of use",
        guidance="State over what period and how often the system is intended to be used.",
    ),
    FriaElement(
        point="c",
        title="Categories of natural persons and groups affected",
        guidance="Identify the categories of natural persons and groups likely to be "
        "affected by its use in the specific context.",
    ),
    FriaElement(
        point="d",
        title="Specific risks of harm",
        guidance="Identify the specific risks of harm likely to affect the categories "
        "identified in (c), taking account of the provider's Art. 13 information.",
    ),
    FriaElement(
        point="e",
        title="Human oversight measures",
        guidance="Describe the implementation of human oversight measures, according to "
        "the instructions for use.",
    ),
    FriaElement(
        point="f",
        title="Measures if the risks materialise",
        guidance="Describe the measures to be taken if those risks materialise, including "
        "internal governance and complaint mechanisms.",
    ),
)

_NOT_REQUIRED = (
    "Art. 27 was not emitted for this profile: the FRIA applies to deployers that are "
    "public bodies or private entities providing public services, using an Annex III "
    "high-risk system other than point 2 (critical infrastructure)."
)


def assess_fria(classification: Classification) -> FriaAssessment:
    """Report whether Art. 27 applies and, if so, the elements to complete."""
    obligation = next((o for o in classification.obligations if o.id == FRIA_OBLIGATION_ID), None)
    if obligation is None:
        return FriaAssessment(
            required=False, reason=_NOT_REQUIRED, effective_date=None, elements=()
        )

    return FriaAssessment(
        required=True,
        reason=(
            f"{obligation.reference} was emitted by the classifier under bundle "
            f"{classification.bundle_version}; it applies from "
            f"{obligation.effective_date.isoformat()}."
        ),
        effective_date=obligation.effective_date,
        elements=FRIA_ELEMENTS,
    )
