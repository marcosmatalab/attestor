"""Golden tests for the bundle in force (reg-2026-1744)."""

import pathlib

import pytest
import yaml

from attestor.classifier import Bundle, SystemProfile, classify, load_bundle

_GOLDEN_PATH = pathlib.Path(__file__).parent / "golden" / "reg-2026-1744.yaml"
_VECTORS = yaml.safe_load(_GOLDEN_PATH.read_text(encoding="utf-8"))["vectors"]


@pytest.fixture(scope="module")
def bundle() -> Bundle:
    return load_bundle("reg-2026-1744")


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_in_force_golden_vector(vector: dict, bundle: Bundle) -> None:
    result = classify(SystemProfile(**vector["input"]), bundle)

    assert result.risk.value == vector["expected"]["risk"]

    actual = {(o.id, o.effective_date.isoformat()) for o in result.obligations}
    expected = {(o["id"], o["effective_date"]) for o in vector["expected"]["obligations"]}
    assert actual == expected
