"""Golden tests for the Digital Omnibus bundle (omnibus-2026)."""

import pathlib

import pytest
import yaml

from attestor.classifier import Bundle, SystemProfile, classify, load_bundle

_GOLDEN_PATH = pathlib.Path(__file__).parent / "golden" / "omnibus-2026.yaml"
_VECTORS = yaml.safe_load(_GOLDEN_PATH.read_text(encoding="utf-8"))["vectors"]


@pytest.fixture(scope="module")
def bundle() -> Bundle:
    return load_bundle("omnibus-2026")


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_omnibus_golden_vector(vector: dict, bundle: Bundle) -> None:
    result = classify(SystemProfile(**vector["input"]), bundle)

    assert result.risk.value == vector["expected"]["risk"]

    actual = {(o.id, o.effective_date.isoformat()) for o in result.obligations}
    expected = {(o["id"], o["effective_date"]) for o in vector["expected"]["obligations"]}
    assert actual == expected
