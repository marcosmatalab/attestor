"""Tests for the ISO/IEC 42001 reference crosswalk."""

from attestor.classifier import Classification, SystemProfile, classify, load_bundle
from attestor.governance import derive_crosswalk
from attestor.governance.iso42001 import (
    ISO_42001_ANNEX_A,
    ISO_42001_CLAUSES,
    OBLIGATION_ISO_MAP,
)

_BUNDLE = load_bundle("v2026-08")


def _high_risk_provider() -> Classification:
    profile = SystemProfile(role="provider", annex_iii_area="employment")
    return classify(profile, _BUNDLE)


def test_crosswalk_derives_entries_for_mapped_obligations() -> None:
    classification = _high_risk_provider()
    crosswalk = derive_crosswalk(classification)

    ids = {entry.obligation_id for entry in crosswalk.entries}
    assert "art9_risk_management" in ids
    assert "art11_technical_documentation" in ids
    # Every entry corresponds to an obligation the classifier actually emitted.
    emitted = {o.id for o in classification.obligations}
    assert ids <= emitted


def test_every_reference_id_is_a_valid_iso_identifier() -> None:
    crosswalk = derive_crosswalk(_high_risk_provider())
    for entry in crosswalk.entries:
        assert entry.iso_references  # mapped obligations have at least one reference
        for ref in entry.iso_references:
            if ref.kind == "clause":
                assert ref.id in ISO_42001_CLAUSES
                assert ref.label == f"Clause {ref.id}"
            else:
                assert ref.kind == "annex_a"
                assert ref.id in ISO_42001_ANNEX_A
                assert ref.label == f"Annex {ref.id}"


def test_annex_a_numbering_is_pinned_to_iso_42001_2023() -> None:
    # Guard against the common secondary-source mistake in the A.5-A.10 range.
    assert ISO_42001_ANNEX_A["A.5"] == "Assessing impacts of AI systems"
    assert ISO_42001_ANNEX_A["A.6"] == "AI system life cycle"
    assert ISO_42001_ANNEX_A["A.8"] == "Information for interested parties of AI systems"
    assert ISO_42001_ANNEX_A["A.9"] == "Use of AI systems"
    assert ISO_42001_ANNEX_A["A.10"] == "Third-party and customer relationships"


def test_only_applied_obligations_appear() -> None:
    # A deployer FRIA classification draws different obligations than a provider.
    profile = SystemProfile(role="deployer", annex_iii_area="credit_scoring")
    crosswalk = derive_crosswalk(classify(profile, _BUNDLE))
    ids = {entry.obligation_id for entry in crosswalk.entries}

    assert "art9_risk_management" not in ids  # provider-only, not emitted for a deployer
    assert "art27_fria" in ids  # FRIA applies and is mapped (Clause 6 + A.5)


def test_unmappable_procedures_are_omitted_not_invented() -> None:
    # Conformity/registration procedures have no defensible 42001 analogue.
    omitted = ("art43_conformity_assessment", "art47_eu_declaration", "art49_registration")
    for obligation_id in omitted:
        assert obligation_id not in OBLIGATION_ISO_MAP


def test_crosswalk_is_deterministic() -> None:
    assert derive_crosswalk(_high_risk_provider()) == derive_crosswalk(_high_risk_provider())


def test_disclaimer_disclaims_conformity() -> None:
    disclaimer = derive_crosswalk(_high_risk_provider()).disclaimer.lower()
    assert "not an audit" in disclaimer
    assert "certification" in disclaimer
    assert "conformity" in disclaimer
