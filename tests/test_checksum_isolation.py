"""The classification checksum must be isolated from input-schema growth.

These tests pin the behaviour that lets F2 (and later phases) add optional input
fields without perturbing the fingerprints of earlier inputs.
"""

from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle


def test_default_valued_fields_are_excluded_from_the_canonical_form() -> None:
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)

    answers = profile.model_dump(mode="json", exclude_defaults=True)

    # Only non-default fields appear; every defaulted optional field is absent.
    assert answers == {"role": "provider", "annex_iii_area": "employment"}
    assert "annex_i_embedded" not in answers
    assert "is_gpai" not in answers


def test_classification_still_resolves_with_trimmed_context() -> None:
    # exclude_defaults trims the context; predicate matching must still hold.
    bundle = load_bundle()
    result = classify(
        SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment), bundle
    )
    assert result.risk.value == "high"
    assert len(result.obligations) == 13


def test_explicit_default_omnibus_fields_do_not_change_checksum() -> None:
    # Guards exclude_defaults vs exclude_unset: a profile with the new Omnibus
    # fields set EXPLICITLY to False must fingerprint identically to one relying on
    # their defaults. Under exclude_unset these would diverge and break determinism.
    bundle = load_bundle()
    defaulted = classify(
        SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment), bundle
    )
    explicit = classify(
        SystemProfile(
            role=Role.provider,
            annex_iii_area=AnnexIIIArea.employment,
            generates_ncii_or_csam=False,
            ncii_csam_safeguards=False,
        ),
        bundle,
    )
    assert defaulted.checksum == explicit.checksum
