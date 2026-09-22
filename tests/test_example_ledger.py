"""The committed ``examples/ledger`` must keep verifying, and keep detecting edits.

This is the gate that stops the README's headline claim from rotting. The example
is an artifact a stranger downloads and checks; if a change to canonicalisation,
to the Merkle construction or to the record schema ever stopped it verifying, the
build has to fail before the visitor finds out.
"""

import json
from pathlib import Path

import pytest

from attestor.ledger import load_ledger, verify_ledger
from attestor.ledger.ledger import RECORDS_FILENAME, SIGNED_ROOT_FILENAME

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "ledger"


@pytest.fixture(scope="module")
def loaded():
    return load_ledger(EXAMPLE)


def test_the_example_is_committed_and_complete() -> None:
    assert (EXAMPLE / RECORDS_FILENAME).is_file()
    assert (EXAMPLE / SIGNED_ROOT_FILENAME).is_file()
    assert (EXAMPLE / "README.md").is_file()


def test_no_private_key_is_committed() -> None:
    """The example is verifiable from public material only. Keep it that way."""
    for path in EXAMPLE.rglob("*"):
        if path.is_file():
            assert "PRIVATE KEY" not in path.read_text(encoding="utf-8", errors="ignore")


def test_the_committed_example_verifies(loaded) -> None:
    records, root = loaded
    result = verify_ledger(records, root)

    assert result.verified is True
    assert result.integrity_ok is True
    assert result.signature_ok is True
    assert result.timestamp_ok is None
    assert result.recomputed_root == root.merkle_root


def test_it_anchors_the_three_pipeline_artifacts(loaded) -> None:
    records, root = loaded
    assert root.leaf_count == len(records) == 3
    assert [r.kind for r in records] == [
        "classification",
        "annex-iv-dossier",
        "c2pa-manifest",
    ]


def test_it_anchors_the_reproducible_classification_checksum(loaded) -> None:
    """Ties the artifact to the engine: the digest is one a reader can recompute."""
    from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle

    records, _ = loaded
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    expected = classify(profile, load_bundle()).checksum

    assert records[0].payload_sha256 == expected


def test_editing_one_byte_flips_the_verdict(tmp_path: Path) -> None:
    for name in (RECORDS_FILENAME, SIGNED_ROOT_FILENAME):
        (tmp_path / name).write_text((EXAMPLE / name).read_text(encoding="utf-8"), encoding="utf-8")

    target = tmp_path / RECORDS_FILENAME
    edited = target.read_text(encoding="utf-8").replace("sys-1", "sys-9")
    target.write_text(edited, encoding="utf-8")

    records, root = load_ledger(tmp_path)
    result = verify_ledger(records, root)

    assert result.integrity_ok is False
    assert result.signature_ok is True  # the root was not touched
    assert result.verified is False


def test_the_files_are_diff_friendly_json() -> None:
    for name in (RECORDS_FILENAME, SIGNED_ROOT_FILENAME):
        text = (EXAMPLE / name).read_text(encoding="utf-8")
        assert text.endswith("\n")
        assert json.loads(text) is not None
