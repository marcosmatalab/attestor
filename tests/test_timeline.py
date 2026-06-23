"""Tests for the dual-scenario timeline comparison."""

from attestor.classifier import (
    AnnexIIIArea,
    ContentLifecycle,
    Role,
    SystemProfile,
    compare_timelines,
    load_bundle,
)
from attestor.classifier.timeline import ObligationTimeline, TimelineComparison


def _row(comparison: TimelineComparison, oid: str) -> ObligationTimeline:
    return next(o for o in comparison.obligations if o.id == oid)


def test_high_risk_annex_iii_dates_diverge_but_risk_does_not() -> None:
    comparison = compare_timelines(
        SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    )
    assert comparison.binding_scenario == "legal-text"
    assert comparison.legal_text_risk.value == "high"
    assert comparison.omnibus_risk.value == "high"
    assert comparison.risk_diverges is False

    art9 = _row(comparison, "art9_risk_management")
    assert str(art9.legal_text_date) == "2026-08-02"
    assert str(art9.omnibus_date) == "2027-12-02"
    assert art9.diverges
    # every high-risk obligation shifted
    assert len(comparison.divergences) == len(comparison.obligations)


def test_unchanged_obligation_does_not_diverge() -> None:
    comparison = compare_timelines(SystemProfile(role=Role.provider, interacts_with_humans=True))
    art50_1 = _row(comparison, "art50_1_chatbot")
    assert str(art50_1.legal_text_date) == "2026-08-02"
    assert str(art50_1.omnibus_date) == "2026-08-02"
    assert not art50_1.diverges
    assert comparison.divergences == ()


def test_intersection_high_risk_and_chatbot_shows_partial_divergence() -> None:
    # The headline value: high-risk dates defer to 2027-12-02, but the Art. 50(1)
    # transparency obligation stays at 2026-08-02 — divergence is per obligation.
    comparison = compare_timelines(
        SystemProfile(
            role=Role.provider,
            annex_iii_area=AnnexIIIArea.employment,
            interacts_with_humans=True,
        )
    )
    assert _row(comparison, "art9_risk_management").diverges
    assert not _row(comparison, "art50_1_chatbot").diverges


def test_nudifier_diverges_from_limited_to_prohibited() -> None:
    comparison = compare_timelines(
        SystemProfile(
            role=Role.provider,
            generates_ncii_or_csam=True,
            generates_synthetic_content=True,
            content_lifecycle=ContentLifecycle.new,
        )
    )
    assert comparison.legal_text_risk.value == "limited"
    assert comparison.omnibus_risk.value == "prohibited"
    assert comparison.risk_diverges

    nudifier = _row(comparison, "art5_nudifier_ncii_csam")
    assert nudifier.legal_text_date is None  # not a prohibition under the legal text
    assert str(nudifier.omnibus_date) == "2026-12-02"


def test_caveat_is_read_from_the_bundle_meta_not_hardcoded() -> None:
    comparison = compare_timelines(SystemProfile(role=Role.provider))
    expected = str(load_bundle("omnibus-2026").meta["status_note"]).strip()
    assert comparison.omnibus_status == expected
    assert "provisional" in comparison.omnibus_status.lower()
