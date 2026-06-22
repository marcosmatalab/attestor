"""Golden tests: the deterministic core of the determinism story.

Each vector pins a system profile to its expected risk tier AND per-obligation
effective date. Any drift in the engine or the bundle fails the build.
"""

import pathlib

import pytest
import yaml

from attestor.classifier import Bundle, SystemProfile, classify, load_bundle

_GOLDEN_PATH = pathlib.Path(__file__).parent / "golden" / "v2026-08.yaml"
_VECTORS = yaml.safe_load(_GOLDEN_PATH.read_text(encoding="utf-8"))["vectors"]


@pytest.fixture(scope="module")
def bundle() -> Bundle:
    return load_bundle()


@pytest.mark.parametrize("vector", _VECTORS, ids=[v["name"] for v in _VECTORS])
def test_golden_vector(vector: dict, bundle: Bundle) -> None:
    result = classify(SystemProfile(**vector["input"]), bundle)

    assert result.risk.value == vector["expected"]["risk"]

    actual = {(o.id, o.effective_date.isoformat()) for o in result.obligations}
    expected = {(o["id"], o["effective_date"]) for o in vector["expected"]["obligations"]}
    assert actual == expected


def test_every_emitted_reference_resolves_in_the_bundle(bundle: Bundle) -> None:
    # Cross-check: every obligation the engine emits carries a reference that the
    # bundle's article index resolves (the contract the F3 citation validator uses).
    for vector in _VECTORS:
        result = classify(SystemProfile(**vector["input"]), bundle)
        for obligation in result.obligations:
            assert obligation.reference in bundle.articles
