"""Unit tests for the classification engine mechanics."""

import pytest

from attestor.classifier import classify, load_bundle
from attestor.classifier.bundle import Bundle
from attestor.classifier.engine import _matches
from attestor.classifier.model import (
    AnnexIIIArea,
    DeployerType,
    ProhibitedPractice,
    RiskTier,
    Role,
    SystemProfile,
)


@pytest.fixture(scope="module")
def bundle() -> Bundle:
    return load_bundle()


# --- predicate matcher -------------------------------------------------------


def test_empty_predicate_always_matches() -> None:
    assert _matches({}, {"a": 1})


def test_scalar_equality() -> None:
    assert _matches({"a": 1}, {"a": 1})
    assert not _matches({"a": 1}, {"a": 2})


def test_membership_in_list() -> None:
    assert _matches({"a": [1, 2]}, {"a": 2})
    assert not _matches({"a": [1, 2]}, {"a": 3})


def test_missing_context_key_does_not_match() -> None:
    assert not _matches({"a": 1}, {})


# --- tier resolution & obligations ------------------------------------------


def test_minimal_system_has_no_obligations(bundle: Bundle) -> None:
    result = classify(SystemProfile(role=Role.provider), bundle)
    assert result.risk is RiskTier.minimal
    assert result.obligations == ()


def test_high_risk_provider_emits_full_annex_iii_set(bundle: Bundle) -> None:
    result = classify(
        SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment), bundle
    )
    assert result.risk is RiskTier.high
    ids = {o.id for o in result.obligations}
    assert ids == {
        "art9_risk_management",
        "art10_data_governance",
        "art11_technical_documentation",
        "art12_record_keeping",
        "art13_transparency_deployers",
        "art14_human_oversight",
        "art15_accuracy_robustness",
        "art16_provider_obligations",
        "art17_quality_management",
        "art43_conformity_assessment",
        "art47_eu_declaration",
        "art48_ce_marking",
        "art49_registration",
    }
    assert "art27_fria" not in ids  # FRIA is a deployer obligation
    assert all(str(o.effective_date) == "2026-08-02" for o in result.obligations)


def test_fria_fires_for_credit_scoring_even_for_private_deployer(bundle: Bundle) -> None:
    # Art. 27 branch B: any deployer of an Annex III 5(b) credit-scoring system.
    result = classify(
        SystemProfile(
            role=Role.deployer,
            annex_iii_area=AnnexIIIArea.credit_scoring,
            deployer_type=DeployerType.other,
        ),
        bundle,
    )
    assert result.risk is RiskTier.high
    ids = {o.id for o in result.obligations}
    assert "art27_fria" in ids


def test_prohibited_short_circuit_drops_other_obligations(bundle: Bundle) -> None:
    # Even with a transparency trigger present, a prohibited system carries only
    # its prohibition obligation; art50_1 (not a prohibition) is dropped.
    result = classify(
        SystemProfile(
            role=Role.provider,
            prohibited_practice=ProhibitedPractice.social_scoring,
            interacts_with_humans=True,
        ),
        bundle,
    )
    assert result.risk is RiskTier.prohibited
    assert [o.id for o in result.obligations] == ["art5_prohibition"]
    assert str(result.obligations[0].effective_date) == "2025-02-02"


def test_conflicting_effective_dates_raise(bundle: Bundle) -> None:
    content = {
        "meta": {"version": "conflict-test"},
        "articles": {"Art. 9": "Risk management system"},
        "risk_tier_rules": [{"id": "minimal", "when": {}, "tier": "minimal"}],
        "obligation_rules": [
            {"obligation": "art9", "when": {}, "effective_date": "2026-08-02"},
            {"obligation": "art9", "when": {}, "effective_date": "2027-08-02"},
        ],
        "obligations": {"art9": {"reference": "Art. 9", "title": "Risk management system"}},
    }
    crafted = Bundle(content)
    with pytest.raises(ValueError, match="conflicting effective_date"):
        classify(SystemProfile(role=Role.provider), crafted)


def test_checksum_reflects_the_result(bundle: Bundle) -> None:
    minimal = classify(SystemProfile(role=Role.provider), bundle)
    prohibited = classify(
        SystemProfile(role=Role.provider, prohibited_practice=ProhibitedPractice.social_scoring),
        bundle,
    )
    assert minimal.checksum != prohibited.checksum


def _category_bundle() -> Bundle:
    """A bundle exercising the category-tagged + legacy-id prohibition mechanism."""
    return Bundle(
        {
            "meta": {"version": "cat-test"},
            "articles": {"Art. 5(1)": "Prohibited", "Art. 50(1)": "Transparency"},
            "risk_tier_rules": [
                {"id": "prohibited", "when": {"nudifier_prohibited": True}, "tier": "prohibited"},
                {"id": "minimal", "when": {}, "tier": "minimal"},
            ],
            "obligation_rules": [
                {
                    "obligation": "art5_prohibition",
                    "when": {"risk_tier": "prohibited"},
                    "effective_date": "2025-02-02",
                },
                {
                    "obligation": "art5_nudifier",
                    "when": {"nudifier_prohibited": True},
                    "effective_date": "2026-12-02",
                },
                {
                    "obligation": "art50_1",
                    "when": {"nudifier_prohibited": True},
                    "effective_date": "2026-08-02",
                },
            ],
            "obligations": {
                # no category -> recognised via the legacy id allowlist
                "art5_prohibition": {"reference": "Art. 5(1)", "title": "Prohibited"},
                # category tag -> recognised as a prohibition
                "art5_nudifier": {
                    "reference": "Art. 5(1)",
                    "title": "Nudifier",
                    "category": "prohibition",
                },
                # not a prohibition -> dropped by the short-circuit even though it fired
                "art50_1": {"reference": "Art. 50(1)", "title": "Transparency"},
            },
        }
    )


def test_short_circuit_keeps_category_and_legacy_prohibitions_only() -> None:
    result = classify(
        SystemProfile(role=Role.provider, generates_ncii_or_csam=True), _category_bundle()
    )
    assert result.risk is RiskTier.prohibited
    assert {o.id for o in result.obligations} == {"art5_prohibition", "art5_nudifier"}


def test_safe_harbour_disables_the_nudifier_prohibition() -> None:
    result = classify(
        SystemProfile(role=Role.provider, generates_ncii_or_csam=True, ncii_csam_safeguards=True),
        _category_bundle(),
    )
    assert result.risk is RiskTier.minimal
    assert result.obligations == ()
