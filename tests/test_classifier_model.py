"""Tests for the classifier domain model."""

from datetime import date

import pytest
from pydantic import ValidationError

from attestor.classifier.model import (
    AppliedObligation,
    Classification,
    ContentLifecycle,
    RiskTier,
    Role,
    SystemProfile,
)


def test_minimal_profile_defaults() -> None:
    profile = SystemProfile(role=Role.provider)
    assert profile.role is Role.provider
    assert profile.prohibited_practice is None
    assert profile.annex_iii_area is None
    assert profile.is_gpai is False


def test_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        SystemProfile(role=Role.provider, not_a_real_field=True)


def test_profile_is_frozen() -> None:
    profile = SystemProfile(role=Role.provider)
    with pytest.raises(ValidationError):
        profile.role = Role.deployer


def test_synthetic_content_requires_lifecycle() -> None:
    with pytest.raises(ValidationError):
        SystemProfile(role=Role.provider, generates_synthetic_content=True)


def test_synthetic_content_with_lifecycle_is_valid() -> None:
    profile = SystemProfile(
        role=Role.provider,
        generates_synthetic_content=True,
        content_lifecycle=ContentLifecycle.legacy,
    )
    assert profile.content_lifecycle is ContentLifecycle.legacy


def test_effective_dates_property() -> None:
    classification = Classification(
        risk=RiskTier.limited,
        obligations=(
            AppliedObligation(
                id="art50_1_chatbot",
                reference="Art. 50(1)",
                title="Disclosure of AI interaction",
                effective_date=date(2026, 8, 2),
            ),
        ),
        bundle_version="v2026-08",
        bundle_sha256="deadbeef",
        checksum="cafef00d",
    )
    assert classification.effective_dates == {"art50_1_chatbot": "2026-08-02"}
