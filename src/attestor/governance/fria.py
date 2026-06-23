"""Fundamental Rights Impact Assessment (Art. 27) scaffold, derived from a classification.

This is a SCAFFOLD, not a completed FRIA — the same relationship the Annex IV generator
(F3) has to a finished technical file. Applicability is NOT re-decided here: the
classifier already emits the ``art27_fria`` obligation exactly when Art. 27 applies (a
deployer that is a public body or a private provider of a public service, for an Annex
III area other than point 2; or ANY deployer of Annex III 5(b) credit scoring / 5(c) life
& health insurance). So generation is GATED on that obligation being present; otherwise it
raises. The scaffold enumerates what Art. 27(1)(a)-(f) requires the deployer to assess,
with explicit placeholders to be filled in after substantive analysis. No LLM, no clock:
the same classification always yields the same scaffold.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from attestor.classifier.model import (
    AnnexIIIArea,
    Classification,
    DeployerType,
    RiskTier,
    SystemProfile,
)

FRIA_OBLIGATION_ID = "art27_fria"

# Art. 27(1)(a)-(f): what the deployer must assess (close paraphrase of the Regulation,
# which is freely reproducible EU law — unlike the ISO standard).
_ART27_REQUIREMENTS: tuple[tuple[str, str], ...] = (
    (
        "a",
        "the deployer's processes in which the high-risk AI system will be used, in line "
        "with its intended purpose",
    ),
    (
        "b",
        "the period of time within which, and the frequency with which, the system is "
        "intended to be used",
    ),
    (
        "c",
        "the categories of natural persons and groups likely to be affected by its use in "
        "the specific context",
    ),
    (
        "d",
        "the specific risks of harm likely to affect those categories, taking into account "
        "the information given by the provider",
    ),
    (
        "e",
        "the human oversight measures to be implemented, according to the instructions for use",
    ),
    (
        "f",
        "the measures to take if those risks materialise, including internal governance and "
        "complaint mechanisms",
    ),
)

_NOTIFY_NOTE = (
    "Once completed, the deployer must notify the market surveillance authority of the "
    "results of the assessment (Art. 27(3))."
)

_DISCLAIMER = (
    "This is a SCAFFOLD derived from the classification, not a completed FRIA. It "
    "enumerates what Art. 27(1) requires the deployer to assess, with placeholders to be "
    "filled in after substantive analysis. Generating it neither constitutes nor "
    "substitutes for the fundamental rights impact assessment."
)


class FriaSection(BaseModel):
    """One Art. 27(1) assessment point, with a placeholder for the deployer to complete."""

    model_config = ConfigDict(frozen=True)

    point: str  # "a".."f"
    requirement: str
    placeholder: str


class FriaScaffold(BaseModel):
    """A traceable FRIA scaffold derived from a deployer classification (Art. 27)."""

    model_config = ConfigDict(frozen=True)

    risk: RiskTier
    annex_iii_area: str | None
    trigger: str  # which Art. 27(1) limb made the FRIA apply
    fria_reference: str  # "Art. 27"
    fria_effective_date: date
    bundle_version: str
    classification_checksum: str
    sections: tuple[FriaSection, ...]
    notify_authority_note: str = _NOTIFY_NOTE
    disclaimer: str = _DISCLAIMER


def generate_fria(profile: SystemProfile, classification: Classification) -> FriaScaffold:
    """Build the Art. 27 FRIA scaffold; raise if the classification does not require one."""
    fria = next((o for o in classification.obligations if o.id == FRIA_OBLIGATION_ID), None)
    if fria is None:
        raise ValueError(
            "FRIA (Art. 27) does not apply to this classification: the classifier did not "
            "emit the art27_fria obligation. Art. 27 binds only deployers that are public "
            "bodies or private providers of public services (Annex III areas other than "
            "point 2), or any deployer of Annex III 5(b) credit scoring or 5(c) life & "
            "health insurance systems."
        )

    sections = tuple(
        FriaSection(
            point=point,
            requirement=requirement,
            placeholder=f"[TO BE COMPLETED by the deployer: assessment of {requirement}]",
        )
        for point, requirement in _ART27_REQUIREMENTS
    )
    return FriaScaffold(
        risk=classification.risk,
        annex_iii_area=profile.annex_iii_area.value if profile.annex_iii_area else None,
        trigger=_trigger(profile),
        fria_reference=fria.reference,
        fria_effective_date=fria.effective_date,
        bundle_version=classification.bundle_version,
        classification_checksum=classification.checksum,
        sections=sections,
    )


def _trigger(profile: SystemProfile) -> str:
    """Describe which Art. 27(1) limb made the FRIA apply (context for the scaffold)."""
    if profile.annex_iii_area in (AnnexIIIArea.credit_scoring, AnnexIIIArea.life_health_insurance):
        return f"any deployer of an Annex III {profile.annex_iii_area.value} system (Art. 27(1))"
    if profile.deployer_type is DeployerType.public_body:
        return "deployer that is a public body (Art. 27(1))"
    if profile.deployer_type is DeployerType.private_public_service:
        return "deployer that is a private provider of a public service (Art. 27(1))"
    return "Art. 27(1)"
