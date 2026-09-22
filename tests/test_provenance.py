"""C2PA signing and verification, and the integrity/trust split that defines it."""

import pytest

from attestor import __version__
from attestor.classifier import (
    AnnexIIIArea,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)
from attestor.provenance import (
    build_manifest,
    build_signer,
    generate_dev_signing_material,
    sign_bytes,
    synthetic_png,
    verify_bytes,
)
from attestor.provenance.manifest import ATTESTOR_ASSERTION_LABEL
from attestor.provenance.verifier import UNTRUSTED_REASON


@pytest.fixture(scope="module")
def classification():
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    return classify(profile, load_bundle("v2026-08"))


@pytest.fixture(scope="module")
def signed_asset(classification) -> bytes:
    manifest = build_manifest(classification, title="t.png", version=__version__)
    return sign_bytes(manifest, synthetic_png(), build_signer(generate_dev_signing_material()))


def test_synthetic_png_is_byte_stable() -> None:
    assert synthetic_png() == synthetic_png()
    assert synthetic_png().startswith(b"\x89PNG\r\n\x1a\n")


def test_synthetic_png_rejects_degenerate_sizes() -> None:
    with pytest.raises(ValueError, match="positive"):
        synthetic_png(0, 10)


def test_manifest_carries_the_classification_not_prose(classification) -> None:
    manifest = build_manifest(classification, title="t.png", version=__version__)
    assertion = next(a for a in manifest["assertions"] if a["label"] == ATTESTOR_ASSERTION_LABEL)

    assert assertion["data"]["classification_checksum"] == classification.checksum
    assert assertion["data"]["bundle_sha256"] == classification.bundle_sha256
    assert len(assertion["data"]["obligations"]) == len(classification.obligations)


def test_created_action_declares_a_digital_source_type(classification) -> None:
    """Omitting it makes the whole manifest invalid, and it is easy to omit."""
    manifest = build_manifest(classification, title="t.png", version=__version__)
    actions = next(a for a in manifest["assertions"] if a["label"] == "c2pa.actions")
    assert actions["data"]["actions"][0]["digitalSourceType"]


def test_signing_embeds_a_readable_credential(signed_asset: bytes) -> None:
    assert len(signed_asset) > len(synthetic_png())
    assert verify_bytes(signed_asset).has_manifest


def test_integrity_and_trust_are_reported_separately(signed_asset: bytes) -> None:
    """The heart of F5: intact, and signed by someone nobody recognises."""
    report = verify_bytes(signed_asset)

    assert report.validation_state == "Valid"
    assert report.integrity_ok is True
    assert report.integrity_failures == ()
    assert report.trusted is False
    assert "signingCredential.untrusted" in report.trust_failures


def test_headline_states_both_axes_and_never_only_one(signed_asset: bytes) -> None:
    headline = verify_bytes(signed_asset).headline

    assert "integrity Valid (manifest intact, claim well-formed)" in headline
    assert f"signer UNTRUSTED ({UNTRUSTED_REASON})" in headline


def test_credential_carries_the_reproducible_checksum(signed_asset, classification) -> None:
    report = verify_bytes(signed_asset)
    assert report.classification_checksum == classification.checksum
    assert report.bundle_sha256 == classification.bundle_sha256


def test_an_asset_with_no_credential_is_not_reported_as_valid() -> None:
    report = verify_bytes(synthetic_png())

    assert report.has_manifest is False
    assert report.integrity_ok is False
    assert report.trusted is False
    assert "no Content Credential found" in report.headline


def test_a_corrupted_credential_is_not_reported_as_intact(signed_asset: bytes) -> None:
    # Flip bytes in the middle of the embedded manifest, not in the PNG header.
    corrupted = bytearray(signed_asset)
    for offset in range(len(corrupted) // 2, len(corrupted) // 2 + 64):
        corrupted[offset] ^= 0xFF

    report = verify_bytes(bytes(corrupted))
    assert report.trusted is False
    assert not (report.has_manifest and report.integrity_ok and not report.integrity_failures)
