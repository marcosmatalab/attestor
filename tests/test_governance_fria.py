"""Tests for the Art. 27 FRIA scaffold (gated on the classification)."""

import pytest

from attestor.classifier import SystemProfile, classify, load_bundle
from attestor.governance import generate_fria

_BUNDLE = load_bundle("v2026-08")


def _fria(profile: SystemProfile):
    return generate_fria(profile, classify(profile, _BUNDLE))


def test_fria_generates_for_public_body_branch_a() -> None:
    # Art. 27(1) limb A: public body, Annex III area other than point 2 (employment).
    profile = SystemProfile(
        role="deployer", deployer_type="public_body", annex_iii_area="employment"
    )
    scaffold = _fria(profile)

    assert scaffold.fria_reference == "Art. 27"
    assert "public body" in scaffold.trigger
    assert tuple(s.point for s in scaffold.sections) == ("a", "b", "c", "d", "e", "f")


def test_fria_generates_for_credit_scoring_branch_b() -> None:
    # Art. 27(1) limb B: ANY deployer of a 5(b) credit-scoring system.
    profile = SystemProfile(role="deployer", deployer_type="other", annex_iii_area="credit_scoring")
    scaffold = _fria(profile)

    assert "credit_scoring" in scaffold.trigger
    assert scaffold.annex_iii_area == "credit_scoring"


def test_every_section_is_an_unfilled_placeholder() -> None:
    profile = SystemProfile(
        role="deployer", deployer_type="public_body", annex_iii_area="employment"
    )
    scaffold = _fria(profile)

    assert len(scaffold.sections) == 6
    for section in scaffold.sections:
        assert section.placeholder.startswith("[TO BE COMPLETED")
        assert section.requirement  # the Art. 27(1) requirement is named
    # It is a scaffold, not a completed FRIA.
    assert "not a completed FRIA" in scaffold.disclaimer
    assert "27(3)" in scaffold.notify_authority_note  # notify the authority once done


def test_gate_rejects_a_provider() -> None:
    # Providers do not draw up a FRIA; the classifier emits no art27_fria.
    profile = SystemProfile(role="provider", annex_iii_area="employment")
    with pytest.raises(ValueError, match="does not apply"):
        _fria(profile)


def test_gate_rejects_excluded_area_point_2() -> None:
    # Critical infrastructure is Annex III point 2 — excluded from the public-body limb,
    # and not a 5(b)/5(c) system, so no FRIA applies even for a public body.
    profile = SystemProfile(
        role="deployer", deployer_type="public_body", annex_iii_area="critical_infrastructure"
    )
    with pytest.raises(ValueError, match="does not apply"):
        _fria(profile)


def test_fria_is_deterministic() -> None:
    profile = SystemProfile(
        role="deployer", deployer_type="public_body", annex_iii_area="employment"
    )
    assert _fria(profile) == _fria(profile)
