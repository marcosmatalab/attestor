"""Deterministic Annex IV dossier generator.

No LLM. The dossier is templated from the fixed Annex IV structure and populated
with the classification's obligations, each placed by the defensible
obligation->section map (unmapped obligations default to the appendix). The same
``SystemProfile`` + ``Classification`` + ``Bundle`` always yields an identical
dossier — the citations are derived from the classification, never asserted.
"""

from attestor.annexiv.model import AnnexIVDossier, Citation, DossierSection
from attestor.annexiv.sections import (
    ANNEX_IV_SECTIONS,
    APPENDIX_SECTION,
    LEGAL_BASIS_OBLIGATION_ID,
    OBLIGATION_SECTION_MAP,
)
from attestor.classifier.bundle import Bundle
from attestor.classifier.model import (
    AppliedObligation,
    Classification,
    RiskTier,
    Role,
    SystemProfile,
)

DEFAULT_SYSTEM_NAME = "[TO BE COMPLETED: system name]"


def generate_dossier(
    profile: SystemProfile,
    classification: Classification,
    bundle: Bundle,
    *,
    system_name: str | None = None,
) -> AnnexIVDossier:
    """Build the Annex IV dossier for a high-risk provider classification."""
    _check_gate(profile, classification, bundle)

    by_id = {o.id: o for o in classification.obligations}
    legal_basis = (
        _as_citation(by_id[LEGAL_BASIS_OBLIGATION_ID])
        if LEGAL_BASIS_OBLIGATION_ID in by_id
        else None
    )

    sections: list[DossierSection] = []
    for number, title, guidance in ANNEX_IV_SECTIONS:
        citations = tuple(
            _as_citation(o)
            for o in classification.obligations
            if number in OBLIGATION_SECTION_MAP.get(o.id, ())
        )
        sections.append(
            DossierSection(number=number, title=title, guidance=guidance, citations=citations)
        )

    # default-to-appendix: any obligation without an explicit section mapping (and
    # that is not the legal basis) is listed in the appendix, so the generator never
    # breaks on new/unmapped obligations and completeness always holds.
    appendix_citations = tuple(
        _as_citation(o)
        for o in classification.obligations
        if o.id != LEGAL_BASIS_OBLIGATION_ID and o.id not in OBLIGATION_SECTION_MAP
    )
    appendix_number, appendix_title, appendix_guidance = APPENDIX_SECTION
    sections.append(
        DossierSection(
            number=appendix_number,
            title=appendix_title,
            guidance=appendix_guidance,
            citations=appendix_citations,
        )
    )

    return AnnexIVDossier(
        system_name=system_name or DEFAULT_SYSTEM_NAME,
        risk=classification.risk,
        scenario=str(bundle.meta.get("scenario", "")),
        bundle_version=classification.bundle_version,
        bundle_sha256=classification.bundle_sha256,
        classification_checksum=classification.checksum,
        legal_basis=legal_basis,
        provisional_note=str(bundle.meta.get("status_note", "")).strip(),
        sections=tuple(sections),
    )


def _check_gate(profile: SystemProfile, classification: Classification, bundle: Bundle) -> None:
    if classification.bundle_version != bundle.version:
        raise ValueError(
            f"classification was produced under bundle {classification.bundle_version!r}, "
            f"not {bundle.version!r}"
        )
    if classification.risk is not RiskTier.high:
        raise ValueError(
            "Annex IV technical documentation applies to high-risk systems only; "
            f"this system is classified {classification.risk.value!r}"
        )
    if profile.role is not Role.provider:
        raise ValueError(
            "Annex IV technical documentation is a provider obligation; deployers do not draw it up"
        )


def _as_citation(obligation: AppliedObligation) -> Citation:
    return Citation(
        obligation_id=obligation.id,
        reference=obligation.reference,
        title=obligation.title,
        effective_date=obligation.effective_date,
    )
