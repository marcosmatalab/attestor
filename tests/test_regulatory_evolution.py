"""The Digital Omnibus became law, and absorbing it left every earlier bundle intact.

This is the test that makes the repository's design claim checkable rather than
rhetorical. Effective dates live **on each obligation**, not as one global date on
the bundle, so a real change in EU law was absorbed by adding a bundle rather
than editing one. Nothing was migrated and not one historical artifact moved by a
byte. (The same commit, 00a566d, did make small engine edits - the timeline's
comparison target and an Annex IV field name; tests/test_claims_match_history.py
keeps the docs honest about that.)

Four assertions, each guarding a different way that could quietly stop being true:

1. the bundle in force declares what it is and since when;
2. the two historical bundles still hash to the values they had in June 2026 -
   if either changes, someone edited an artifact whose digest is anchored, which
   is the one thing an evidence system must never do;
3. the dates the proposal was modelled with are exactly the dates that became law;
4. the frozen provisional bundle still describes the situation it described.
"""

import pathlib

import pytest
import yaml

from attestor.classifier import SystemProfile, classify, load_bundle

# Measured on 2026-06-23 and unchanged since. These literals are the point of the
# test: they must be typed, never computed from the files they are checking.
LEGAL_TEXT_SHA256 = "7e77bc0715a2b5836f83e6c50e69ab312ca8b7167c1c747674d8143a3312d49d"
OMNIBUS_SHA256 = "a52cb5e185c01fa0cf62b967a659d5cc8e7769b176e25b3eb2e9647299462c51"

IN_FORCE_SINCE = "2026-07-27"

_GOLDEN = pathlib.Path(__file__).parent / "golden" / "omnibus-2026.yaml"
_VECTORS = yaml.safe_load(_GOLDEN.read_text(encoding="utf-8"))["vectors"]


def test_the_bundle_in_force_declares_what_it_is() -> None:
    bundle = load_bundle("reg-2026-1744")

    assert bundle.meta["status"] == "in-force"
    assert bundle.meta["in_force_since"] == IN_FORCE_SINCE
    assert "2026/1744" in bundle.meta["regulation"]
    assert bundle.version == load_bundle().version, "it must also be the default"


@pytest.mark.parametrize(
    ("version", "expected_sha256"),
    [("v2026-08", LEGAL_TEXT_SHA256), ("omnibus-2026", OMNIBUS_SHA256)],
)
def test_historical_bundles_were_not_touched(version: str, expected_sha256: str) -> None:
    """Adding the bundle in force changed no byte of any earlier bundle."""
    assert load_bundle(version).sha256 == expected_sha256


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_what_was_modelled_as_a_proposal_is_what_became_law(vector: dict) -> None:
    """Every date modelled on 2026-06-23 matches the adopted text, one by one."""
    profile = SystemProfile(**vector["input"])
    provisional = classify(profile, load_bundle("omnibus-2026"))
    in_force = classify(profile, load_bundle("reg-2026-1744"))

    assert in_force.risk == provisional.risk
    assert in_force.effective_dates == provisional.effective_dates


def test_the_provisional_bundle_still_says_it_was_provisional() -> None:
    """It described a situation that was real on 2026-06-23. That stays true."""
    note = load_bundle("omnibus-2026").meta["status_note"]

    assert "provisional" in note.lower()
    assert load_bundle("omnibus-2026").meta["status"] == "pending-formal-adoption"


def test_the_three_scenarios_are_distinguishable_by_content_hash() -> None:
    """Three bundles, three identities. A scenario is never a mutation of another."""
    digests = {v: load_bundle(v).sha256 for v in ("v2026-08", "omnibus-2026", "reg-2026-1744")}
    assert len(set(digests.values())) == 3
