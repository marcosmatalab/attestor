"""Domain model for the Annex IV dossier.

Section titles and guidance are fixed template text from the Annex IV structure
(they may name articles, as the Regulation itself does). Only ``Citation`` objects
are derived from the classification and validated.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from attestor.classifier.model import RiskTier


class Citation(BaseModel):
    """A derived, validated reference to one obligation the classifier emitted."""

    model_config = ConfigDict(frozen=True)

    obligation_id: str
    reference: str
    title: str
    effective_date: date


class DossierSection(BaseModel):
    """One Annex IV point (number ``"1"``..``"9"``) or the appendix (``"A"``)."""

    model_config = ConfigDict(frozen=True)

    number: str
    title: str
    guidance: str
    citations: tuple[Citation, ...]


class AnnexIVDossier(BaseModel):
    """A traceable Annex IV scaffold derived from a high-risk classification."""

    model_config = ConfigDict(frozen=True)

    system_name: str
    risk: RiskTier
    scenario: str
    bundle_version: str
    bundle_sha256: str
    classification_checksum: str
    legal_basis: Citation | None  # Article 11 — the basis for this very document
    # Regulatory status of the bundle this dossier was drawn up under, read from its
    # ``meta`` and never composed here. It was named ``provisional_note`` while the
    # only non-empty value was a provisional caveat; once the Omnibus became law the
    # name would have made a dossier state the opposite of the truth.
    status_note: str
    sections: tuple[DossierSection, ...]

    @property
    def all_citations(self) -> tuple[Citation, ...]:
        """Every derived citation: the legal basis plus all section citations."""
        cites: list[Citation] = []
        if self.legal_basis is not None:
            cites.append(self.legal_basis)
        for section in self.sections:
            cites.extend(section.citations)
        return tuple(cites)
