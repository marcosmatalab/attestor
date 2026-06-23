"""Tests for the Annex IV section templates and dossier model."""

from datetime import date

from attestor.annexiv.model import AnnexIVDossier, Citation, DossierSection
from attestor.annexiv.sections import (
    ANNEX_IV_SECTIONS,
    LEGAL_BASIS_OBLIGATION_ID,
    OBLIGATION_SECTION_MAP,
)
from attestor.classifier.model import RiskTier


def test_there_are_nine_annex_iv_sections_numbered_1_to_9() -> None:
    numbers = [number for number, _, _ in ANNEX_IV_SECTIONS]
    assert numbers == ["1", "2", "3", "4", "5", "6", "7", "8", "9"]


def test_mapping_only_targets_real_section_numbers() -> None:
    valid = {number for number, _, _ in ANNEX_IV_SECTIONS}
    for sections in OBLIGATION_SECTION_MAP.values():
        assert set(sections) <= valid


def test_legal_basis_obligation_is_article_11() -> None:
    assert LEGAL_BASIS_OBLIGATION_ID == "art11_technical_documentation"


def _cite(oid: str) -> Citation:
    return Citation(
        obligation_id=oid, reference="Art. 9", title="x", effective_date=date(2026, 8, 2)
    )


def test_all_citations_includes_legal_basis_and_section_citations() -> None:
    dossier = AnnexIVDossier(
        system_name="[placeholder]",
        risk=RiskTier.high,
        scenario="legal-text",
        bundle_version="v2026-08",
        bundle_sha256="deadbeef",
        classification_checksum="cafef00d",
        legal_basis=_cite("art11_technical_documentation"),
        provisional_note="",
        sections=(
            DossierSection(
                number="5", title="Risk", guidance="g", citations=(_cite("art9_risk_management"),)
            ),
        ),
    )
    ids = {c.obligation_id for c in dossier.all_citations}
    assert ids == {"art11_technical_documentation", "art9_risk_management"}
