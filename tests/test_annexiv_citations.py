"""Tests for the fail-closed Annex IV citation validator."""

from datetime import date

import pytest

from attestor.annexiv import generate_dossier, validate_citations
from attestor.annexiv.citations import CitationError
from attestor.annexiv.model import AnnexIVDossier, Citation, DossierSection
from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle

BUNDLE = load_bundle("v2026-08")
PROFILE = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
CLASSIFICATION = classify(PROFILE, BUNDLE)


def _dossier(
    citations: tuple[Citation, ...], *, legal_basis: Citation | None = None
) -> AnnexIVDossier:
    return AnnexIVDossier(
        system_name="x",
        risk=CLASSIFICATION.risk,
        scenario="legal-text",
        bundle_version="v2026-08",
        bundle_sha256="x",
        classification_checksum="x",
        legal_basis=legal_basis,
        provisional_note="",
        sections=(DossierSection(number="5", title="t", guidance="g", citations=citations),),
    )


def _cite(obligation_id: str, reference: str) -> Citation:
    return Citation(
        obligation_id=obligation_id, reference=reference, title="x", effective_date=date(2026, 8, 2)
    )


def test_generated_dossier_passes_validation() -> None:
    dossier = generate_dossier(PROFILE, CLASSIFICATION, BUNDLE)
    validate_citations(dossier, CLASSIFICATION, BUNDLE)  # must not raise


def test_unresolved_reference_fails() -> None:
    dossier = _dossier((_cite("art9_risk_management", "Art. 999"),))
    with pytest.raises(CitationError, match="unresolved citation"):
        validate_citations(dossier, CLASSIFICATION, BUNDLE)


def test_orphan_citation_fails() -> None:
    # Resolvable reference, but the obligation was never emitted by the classifier.
    dossier = _dossier((_cite("ghost_obligation", "Art. 9"),))
    with pytest.raises(CitationError, match="orphan citation"):
        validate_citations(dossier, CLASSIFICATION, BUNDLE)


def test_incomplete_dossier_fails() -> None:
    # Cites only one real obligation; the other 12 are missing.
    dossier = _dossier((_cite("art9_risk_management", "Art. 9"),))
    with pytest.raises(CitationError, match="incomplete dossier"):
        validate_citations(dossier, CLASSIFICATION, BUNDLE)
