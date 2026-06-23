"""Integrity tests for the regulatory bundle and its loader."""

import pytest

from attestor.classifier.bundle import Bundle, load_bundle


def test_default_bundle_loads_and_is_versioned() -> None:
    bundle = load_bundle()
    assert bundle.version == "v2026-08"
    assert bundle.content["meta"]["scenario"] == "legal-text"


def test_bundle_sha256_is_hex_digest() -> None:
    bundle = load_bundle()
    assert len(bundle.sha256) == 64
    assert all(c in "0123456789abcdef" for c in bundle.sha256)


def test_bundle_sha256_is_deterministic() -> None:
    assert load_bundle().sha256 == load_bundle().sha256


def test_every_obligation_rule_targets_a_known_obligation() -> None:
    bundle = load_bundle()
    for rule in bundle.obligation_rules:
        assert rule["obligation"] in bundle.obligations


def test_every_obligation_reference_resolves_in_article_index() -> None:
    # This is the invariant the F3 citation validator will depend on.
    bundle = load_bundle()
    for oid, meta in bundle.obligations.items():
        assert meta["reference"] in bundle.articles, oid


def test_no_omnibus_date_leaked_into_legal_text_bundle() -> None:
    # The 2026-12-02 legacy-marking transition is an Omnibus delta (F2), not legal text.
    bundle = load_bundle()
    dates = {rule["effective_date"] for rule in bundle.obligation_rules}
    assert "2026-12-02" not in dates


def test_unknown_obligation_reference_is_rejected() -> None:
    content = {
        "meta": {"version": "test"},
        "articles": {"Art. 9": "Risk management system"},
        "risk_tier_rules": [],
        "obligation_rules": [],
        "obligations": {"artX": {"reference": "Art. 999", "title": "Bogus"}},
    }
    with pytest.raises(ValueError, match="unresolved reference"):
        Bundle(content)


def test_obligation_rule_with_unknown_obligation_is_rejected() -> None:
    content = {
        "meta": {"version": "test"},
        "articles": {"Art. 9": "Risk management system"},
        "risk_tier_rules": [],
        "obligation_rules": [{"obligation": "ghost", "effective_date": "2026-08-02"}],
        "obligations": {},
    }
    with pytest.raises(ValueError, match="unknown obligation"):
        Bundle(content)


def test_missing_top_level_key_is_rejected() -> None:
    with pytest.raises(ValueError, match="missing top-level keys"):
        Bundle({"meta": {"version": "test"}})


# --- Omnibus bundle (F2) -----------------------------------------------------


def test_omnibus_bundle_loads_with_provisional_status() -> None:
    bundle = load_bundle("omnibus-2026")
    assert bundle.version == "omnibus-2026"
    assert bundle.meta["scenario"] == "omnibus"
    assert bundle.meta["status"] == "pending-formal-adoption"
    assert bundle.meta["status_note"].strip()  # single source of truth for the caveat


def test_omnibus_obligations_and_references_are_consistent() -> None:
    bundle = load_bundle("omnibus-2026")
    for rule in bundle.obligation_rules:
        assert rule["obligation"] in bundle.obligations
    for meta in bundle.obligations.values():
        assert meta["reference"] in bundle.articles


def test_omnibus_nudifier_prohibition_is_categorised() -> None:
    bundle = load_bundle("omnibus-2026")
    nudifier = bundle.obligations["art5_nudifier_ncii_csam"]
    assert nudifier["reference"] == "Art. 5(1)"
    assert nudifier["category"] == "prohibition"


def test_omnibus_and_legal_text_have_distinct_content_hashes() -> None:
    assert load_bundle("omnibus-2026").sha256 != load_bundle("v2026-08").sha256
