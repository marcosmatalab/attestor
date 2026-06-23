"""Golden tests for the Annex IV dossier: pinned sections, citations and dates."""

import pathlib

import pytest
import yaml

from attestor.annexiv import generate_dossier
from attestor.classifier import SystemProfile, classify, load_bundle

_GOLDEN_PATH = pathlib.Path(__file__).parent / "golden" / "annexiv-v2026-08.yaml"
_CASES = yaml.safe_load(_GOLDEN_PATH.read_text(encoding="utf-8"))["cases"]


def _build(case: dict):
    bundle = load_bundle(case["bundle"])
    profile = SystemProfile(**case["input"])
    return generate_dossier(profile, classify(profile, bundle), bundle)


@pytest.mark.parametrize("case", _CASES, ids=[c["name"] for c in _CASES])
def test_annexiv_golden(case: dict) -> None:
    dossier = _build(case)
    expected = case["expected"]

    assert dossier.risk.value == expected["risk"]
    assert dossier.scenario == expected["scenario"]
    assert bool(dossier.provisional_note) == expected["provisional_note"]

    assert dossier.legal_basis is not None
    assert dossier.legal_basis.obligation_id == expected["legal_basis"]["id"]
    assert dossier.legal_basis.reference == expected["legal_basis"]["reference"]
    assert (
        dossier.legal_basis.effective_date.isoformat() == expected["legal_basis"]["effective_date"]
    )

    actual = {
        s.number: {(c.obligation_id, c.effective_date.isoformat()) for c in s.citations}
        for s in dossier.sections
    }
    expected_sections = {
        number: {(oid, day) for oid, day in rows} for number, rows in expected["sections"].items()
    }
    assert actual == expected_sections


@pytest.mark.parametrize("case", _CASES, ids=[c["name"] for c in _CASES])
def test_dossier_generation_is_deterministic(case: dict) -> None:
    assert _build(case) == _build(case)
