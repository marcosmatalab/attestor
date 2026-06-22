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
