"""Governance views: ISO/IEC 42001 map, Art. 27 FRIA, Art. 12 / 26(6) logs."""

import pytest

from attestor.classifier import (
    AnnexIIIArea,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)
from attestor.classifier.model import DeployerType
from attestor.governance import (
    FRIA_ELEMENTS,
    ISO_42001_MAP,
    MINIMUM_RETENTION_MONTHS,
    assess_fria,
    log_retention_duties,
    map_to_iso42001,
)

BUNDLE = "v2026-08"


def classify_profile(**kwargs) -> object:
    return classify(SystemProfile(**kwargs), load_bundle(BUNDLE))


@pytest.fixture
def provider_high():
    return classify_profile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)


@pytest.fixture
def public_deployer():
    return classify_profile(
        role=Role.deployer,
        annex_iii_area=AnnexIIIArea.employment,
        deployer_type=DeployerType.public_body,
    )


def test_every_obligation_is_mapped_or_reported_unmapped(provider_high) -> None:
    """The view may be incomplete; it may never look more complete than it is."""
    result = map_to_iso42001(provider_high)
    accounted = {m.obligation_id for m in result.mappings} | set(result.unmapped_obligations)

    assert accounted == {o.id for o in provider_high.obligations}


def test_mapping_carries_the_classification_identity(provider_high) -> None:
    result = map_to_iso42001(provider_high)
    assert result.classification_checksum == provider_high.checksum
    assert result.bundle_sha256 == provider_high.bundle_sha256


def test_mapping_is_stably_ordered(provider_high) -> None:
    first = map_to_iso42001(provider_high)
    assert list(first.mappings) == sorted(
        first.mappings, key=lambda m: (m.iso_clause, m.obligation_id)
    )
    assert first.model_dump() == map_to_iso42001(provider_high).model_dump()


def test_every_mapping_states_a_rationale() -> None:
    """A mapping without a reason is an assertion, and this repo does not assert."""
    for clause, title, rationale in ISO_42001_MAP.values():
        assert clause and title
        assert len(rationale) > 40


def test_fria_applies_to_a_public_deployer(public_deployer) -> None:
    result = assess_fria(public_deployer)

    assert result.required is True
    assert result.effective_date is not None
    assert len(result.elements) == 6
    assert [e.point for e in result.elements] == list("abcdef")


def test_fria_does_not_apply_to_a_provider(provider_high) -> None:
    result = assess_fria(provider_high)

    assert result.required is False
    assert result.elements == ()
    assert result.effective_date is None
    assert "deployers" in result.reason


def test_fria_date_comes_from_the_classifier_not_from_here(public_deployer) -> None:
    obligation = next(o for o in public_deployer.obligations if o.id == "art27_fria")
    assert assess_fria(public_deployer).effective_date == obligation.effective_date


def test_fria_elements_cover_article_27_1() -> None:
    assert len(FRIA_ELEMENTS) == 6
    assert all(element.guidance for element in FRIA_ELEMENTS)


def test_provider_carries_the_article_12_logging_duty(provider_high) -> None:
    duties = log_retention_duties(provider_high)
    assert [d.obligation_id for d in duties] == ["art12_record_keeping"]
    assert duties[0].minimum_retention_months == MINIMUM_RETENTION_MONTHS


def test_deployer_carries_the_article_26_6_retention_duty(public_deployer) -> None:
    duties = log_retention_duties(public_deployer)
    assert [d.obligation_id for d in duties] == ["art26_6_log_retention"]
    assert "at least six months" in duties[0].note


def test_no_retention_duty_when_no_logging_obligation_applies() -> None:
    minimal = classify_profile(role=Role.provider)
    assert log_retention_duties(minimal) == ()
