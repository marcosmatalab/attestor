"""Tests for the deterministic Annex IV dossier generator."""

import pytest

from attestor.annexiv import generate_dossier
from attestor.classifier import (
    AnnexIIIArea,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)


def _sections_by_number(dossier) -> dict[str, set[tuple[str, str]]]:
    return {
        s.number: {(c.obligation_id, c.effective_date.isoformat()) for c in s.citations}
        for s in dossier.sections
    }


def test_high_risk_provider_dossier_places_obligations() -> None:
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    dossier = generate_dossier(profile, classify(profile, bundle), bundle)

    assert dossier.risk.value == "high"
    assert dossier.scenario == "legal-text"
    assert dossier.provisional_note == ""
    assert dossier.legal_basis is not None
    assert dossier.legal_basis.obligation_id == "art11_technical_documentation"

    by_number = _sections_by_number(dossier)
    assert ("art9_risk_management", "2026-08-02") in by_number["5"]
    assert ("art47_eu_declaration", "2026-08-02") in by_number["8"]
    assert ("art48_ce_marking", "2026-08-02") in by_number["8"]
    # art13/14/15 are placed in more than one section
    assert ("art13_transparency_deployers", "2026-08-02") in by_number["1"]
    assert ("art13_transparency_deployers", "2026-08-02") in by_number["3"]
    # art16/art17/art49 default to the appendix
    assert {oid for oid, _ in by_number["A"]} == {
        "art16_provider_obligations",
        "art17_quality_management",
        "art49_registration",
    }


def test_dossier_is_complete_every_obligation_appears_once() -> None:
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, bundle)
    dossier = generate_dossier(profile, classification, bundle)

    cited = {c.obligation_id for c in dossier.all_citations}
    assert cited == {o.id for o in classification.obligations}


def test_gpai_obligation_falls_to_the_appendix() -> None:
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(
        role=Role.provider, annex_iii_area=AnnexIIIArea.biometrics, is_gpai=True
    )
    dossier = generate_dossier(profile, classify(profile, bundle), bundle)

    appendix = next(s for s in dossier.sections if s.number == "A")
    assert "gpai_art53_documentation" in {c.obligation_id for c in appendix.citations}


def test_omnibus_dossier_carries_provisional_note_and_deferred_dates() -> None:
    bundle = load_bundle("omnibus-2026")
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    dossier = generate_dossier(profile, classify(profile, bundle), bundle)

    assert dossier.scenario == "omnibus"
    assert "provisional" in dossier.provisional_note.lower()
    section5 = next(s for s in dossier.sections if s.number == "5")
    assert section5.citations[0].effective_date.isoformat() == "2027-12-02"


def test_deployer_high_risk_is_rejected() -> None:
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(role=Role.deployer, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, bundle)
    with pytest.raises(ValueError, match="provider obligation; deployers do not draw it up"):
        generate_dossier(profile, classification, bundle)


def test_non_high_risk_is_rejected() -> None:
    bundle = load_bundle("v2026-08")
    profile = SystemProfile(role=Role.provider, interacts_with_humans=True)
    classification = classify(profile, bundle)
    with pytest.raises(ValueError, match="high-risk systems only"):
        generate_dossier(profile, classification, bundle)


def test_bundle_mismatch_is_rejected() -> None:
    legal = load_bundle("v2026-08")
    omnibus = load_bundle("omnibus-2026")
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, legal)  # produced under v2026-08
    with pytest.raises(ValueError, match="not 'omnibus-2026'"):
        generate_dossier(profile, classification, omnibus)
