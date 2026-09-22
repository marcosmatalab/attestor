"""The committed ``examples/ledger`` must keep verifying, and keep detecting edits.

This is the gate that stops the README's headline claim from rotting. The example is
an artifact a stranger downloads and checks; if a change to canonicalisation, to the
Merkle construction or to the record shape ever stopped it verifying, the build has
to fail before the visitor finds out.
"""

import json
from pathlib import Path

import pytest

from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle
from attestor.ledger import load_ledger, verify_ledger

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "ledger"


@pytest.fixture(scope="module")
def loaded() -> tuple[list[dict], object]:
    return load_ledger(EXAMPLE)


def test_the_example_is_committed_and_complete() -> None:
    assert (EXAMPLE / "records.json").is_file()
    assert (EXAMPLE / "signed_root.json").is_file()
    assert (EXAMPLE / "README.md").is_file()


def test_no_private_key_is_committed() -> None:
    """The example is verifiable from public material only. Keep it that way."""
    for path in EXAMPLE.rglob("*"):
        if path.is_file():
            assert "PRIVATE KEY" not in path.read_text(encoding="utf-8", errors="ignore")


def test_the_committed_example_verifies(loaded) -> None:
    records, signed_root = loaded
    result = verify_ledger(records, signed_root)

    assert result.verified is True
    assert result.integrity_ok is True
    assert result.signature_ok is True
    assert result.has_timestamp is False
    assert result.headline.startswith("ledger VERIFIED")


def test_it_anchors_the_three_pipeline_artifacts(loaded) -> None:
    records, signed_root = loaded

    assert signed_root.leaf_count == len(records) == 3
    assert [r["type"] for r in records] == ["classification", "annex_iv", "c2pa_manifest"]


def test_it_anchors_the_reproducible_classification_checksum(loaded) -> None:
    """Ties the artifact to the engine: the digest is one a reader can recompute."""
    records, _ = loaded
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    bundle = load_bundle()

    assert records[0]["checksum"] == classify(profile, bundle).checksum
    assert records[0]["bundle"] == bundle.version
    assert records[0]["bundle_sha256"] == bundle.sha256


def test_editing_one_byte_flips_the_verdict(tmp_path: Path) -> None:
    for name in ("records.json", "signed_root.json"):
        (tmp_path / name).write_text((EXAMPLE / name).read_text(encoding="utf-8"), encoding="utf-8")

    target = tmp_path / "records.json"
    target.write_text(
        target.read_text(encoding="utf-8").replace("sys-1", "sys-9"), encoding="utf-8"
    )

    records, signed_root = load_ledger(tmp_path)
    result = verify_ledger(records, signed_root)

    assert result.integrity_ok is False
    assert result.signature_ok is True  # the signed root was not touched
    assert result.verified is False


def test_the_files_are_parseable_json(loaded) -> None:
    for name in ("records.json", "signed_root.json"):
        assert json.loads((EXAMPLE / name).read_text(encoding="utf-8")) is not None
