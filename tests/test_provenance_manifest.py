"""Tests for the C2PA provenance manifest builder."""

from attestor.provenance import ProvenanceMetadata, build_manifest
from attestor.provenance.manifest import TRAINED_ALGORITHMIC_MEDIA


def test_manifest_has_the_expected_assertions() -> None:
    manifest = build_manifest(ProvenanceMetadata(title="x.png", model="claude-opus-4-8"))

    assert manifest["claim_generator_info"] == [{"name": "attestor", "version": "0.0.1"}]
    labels = [a["label"] for a in manifest["assertions"]]
    assert labels == ["c2pa.actions.v2", "com.attestor.ai_disclosure"]

    action = manifest["assertions"][0]["data"]["actions"][0]
    assert action["action"] == "c2pa.created"
    assert action["digitalSourceType"] == TRAINED_ALGORITHMIC_MEDIA
    assert action["softwareAgent"] == {"name": "attestor/0.0.1"}  # object in v2, not a string

    disclosure = manifest["assertions"][1]["data"]
    assert disclosure["ai_generated"] is True
    assert disclosure["eu_ai_act_art50"] is True
    assert disclosure["model"] == "claude-opus-4-8"


def test_non_ai_manifest_omits_the_digital_source_type() -> None:
    manifest = build_manifest(ProvenanceMetadata(title="x.png", ai_generated=False))
    action = manifest["assertions"][0]["data"]["actions"][0]
    assert "digitalSourceType" not in action
    assert manifest["assertions"][1]["data"]["ai_generated"] is False


def test_manifest_is_deterministic() -> None:
    metadata = ProvenanceMetadata(title="x.png", model="m")
    assert build_manifest(metadata) == build_manifest(metadata)
