"""Literal digests, checked one by one.

The rest of the suite proves the engine agrees with itself: golden vectors pin
risk and dates, and the determinism tests compare a run against another run. None
of that would notice a change to the canonical form, because both sides of every
comparison would move together - and the reproducible checksum is the thing this
repository actually sells to an auditor.

So these values are typed out in ``tests/golden/checksums.yaml`` and compared
against live engine output. If a digest here changes, either the change was
intended and the file is updated deliberately, or something silently broke the
promise that the same input yields the same checksum forever.
"""

import pathlib

import pytest
import yaml

from attestor.classifier import SystemProfile, classify, load_bundle

_ANCHORS = yaml.safe_load(
    (pathlib.Path(__file__).parent / "golden" / "checksums.yaml").read_text(encoding="utf-8")
)

_BUNDLE_CASES = sorted(_ANCHORS["bundles"].items())
_CLASSIFICATION_CASES = [
    (name, case["input"], version, expected)
    for name, case in sorted(_ANCHORS["classifications"].items())
    for version, expected in sorted(case["expected"].items())
]


@pytest.mark.parametrize(("version", "expected"), _BUNDLE_CASES)
def test_bundle_digest_is_anchored(version: str, expected: str) -> None:
    """A bundle's identity is its content hash. These must never drift."""
    assert load_bundle(version).sha256 == expected


@pytest.mark.parametrize(
    ("name", "profile", "version", "expected"),
    _CLASSIFICATION_CASES,
    ids=[f"{name}-{version}" for name, _, version, _ in _CLASSIFICATION_CASES],
)
def test_classification_checksum_is_anchored(
    name: str, profile: dict, version: str, expected: str
) -> None:
    assert classify(SystemProfile(**profile), load_bundle(version)).checksum == expected


def test_the_anchor_file_covers_every_shipped_bundle() -> None:
    """A new bundle must not be able to ship without anchored digests."""
    from attestor.classifier.bundle import available_versions

    assert set(_ANCHORS["bundles"]) == set(available_versions())
    for case in _ANCHORS["classifications"].values():
        assert set(case["expected"]) == set(available_versions())


def test_each_scenario_gives_a_distinct_digest_for_the_same_input() -> None:
    """If two scenarios produced one digest, the checksum would not identify the law."""
    for name, case in _ANCHORS["classifications"].items():
        digests = set(case["expected"].values())
        assert len(digests) > 1, f"{name} produced one digest across all scenarios"
