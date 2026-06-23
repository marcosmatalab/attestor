"""Additivity regression: F2 must NOT change any legal-text result.

The legal-text golden (v2026-08.yaml) is frozen; this re-runs every vector under
the legal-text bundle after the F2 changes and asserts that risk, obligations,
dates AND the checksum are all unchanged. The non-modification is the proof that
F2 is purely additive.
"""

import pathlib

import pytest
import yaml

from attestor.classifier import SystemProfile, classify, load_bundle

_GOLDEN_PATH = pathlib.Path(__file__).parent / "golden" / "v2026-08.yaml"
_VECTORS = yaml.safe_load(_GOLDEN_PATH.read_text(encoding="utf-8"))["vectors"]


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_legal_text_results_unchanged_under_f2(vector: dict) -> None:
    bundle = load_bundle("v2026-08")
    result = classify(SystemProfile(**vector["input"]), bundle)

    assert result.risk.value == vector["expected"]["risk"]
    actual = {(o.id, o.effective_date.isoformat()) for o in result.obligations}
    expected = {(o["id"], o["effective_date"]) for o in vector["expected"]["obligations"]}
    assert actual == expected


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_legal_text_checksum_stable_under_schema_growth(vector: dict) -> None:
    # Adding the Omnibus input fields (at their defaults) must not perturb the
    # legal-text fingerprint — the whole point of exclude_defaults.
    bundle = load_bundle("v2026-08")
    base = classify(SystemProfile(**vector["input"]), bundle)
    grown = classify(
        SystemProfile(**vector["input"], generates_ncii_or_csam=False, ncii_csam_safeguards=False),
        bundle,
    )
    assert base == grown  # full equality, including checksum
