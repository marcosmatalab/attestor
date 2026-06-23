"""Deterministic classification engine.

No LLM, no randomness, no clock: given the same ``SystemProfile`` and the same
``Bundle``, ``classify`` always returns the same ``Classification``. The output
carries a ``checksum`` over the canonical (answers + bundle content hash + result)
so an auditor can reproduce and verify the decision independently.
"""

from datetime import date
from typing import Any

from attestor.canonical import canonical_json, sha256_hex
from attestor.classifier.bundle import Bundle
from attestor.classifier.model import (
    AnnexIIIArea,
    AppliedObligation,
    Classification,
    RiskTier,
    SystemProfile,
)

# A prohibited system is just that — it must not be placed on the market. Its
# headline classification carries only its prohibition obligation(s); any other
# transparency or high-risk obligations are moot. Prohibition obligations are
# identified by ``category: prohibition`` in the bundle catalog (see
# ``_is_prohibition``). The frozen legal-text bundle (v2026-08) predates that
# convention and cannot carry the metadata without changing its content hash, so
# its single prohibition obligation is recognised via this explicit id allowlist.
_LEGACY_PROHIBITION_IDS = frozenset({"art5_prohibition"})
_PROHIBITION_CATEGORY = "prohibition"


def classify(profile: SystemProfile, bundle: Bundle) -> Classification:
    """Classify ``profile`` against ``bundle`` deterministically."""
    # exclude_defaults (NOT exclude_unset) keeps the canonical fingerprint stable as
    # the input schema grows: a field left at its default is absent from the canonical
    # form, so adding new optional fields never perturbs the checksum of older inputs.
    # exclude_unset would break determinism — two semantically equal profiles (one
    # built with explicit defaults, one relying on them) would serialize differently.
    answers = profile.model_dump(mode="json", exclude_defaults=True)
    context = _build_context(profile, answers)

    risk = _resolve_tier(context, bundle)
    context["risk_tier"] = risk.value

    obligations = _resolve_obligations(context, bundle)
    if risk is RiskTier.prohibited:
        obligations = _apply_prohibited_short_circuit(obligations, bundle)

    # Stable order (by id) so the output and its checksum are reproducible
    # regardless of rule order in the bundle.
    obligations.sort(key=lambda o: o.id)

    checksum = _compute_checksum(answers, bundle.sha256, risk, obligations)

    return Classification(
        risk=risk,
        obligations=tuple(obligations),
        bundle_version=bundle.version,
        bundle_sha256=bundle.sha256,
        checksum=checksum,
    )


def _build_context(profile: SystemProfile, answers: dict[str, Any]) -> dict[str, Any]:
    """Augment the raw answers with the derived flags the rules predicate on."""
    context = dict(answers)
    context["has_prohibited_practice"] = profile.prohibited_practice is not None
    context["has_annex_iii_area"] = profile.annex_iii_area is not None
    context["any_art50_trigger"] = (
        profile.interacts_with_humans
        or profile.generates_synthetic_content
        or profile.informs_emotion_biometric
        or profile.generates_deepfakes
    )
    # FRIA branch A excludes Annex III point 2 (critical infrastructure).
    context["fria_eligible_area"] = (
        profile.annex_iii_area is not None
        and profile.annex_iii_area is not AnnexIIIArea.critical_infrastructure
    )
    # Digital Omnibus (Art. 5 NCII/CSAM): prohibited unless the system has adequate
    # safeguards (the safe harbour). Read only by the Omnibus bundle; the legal-text
    # bundle does not reference this flag.
    context["nudifier_prohibited"] = (
        profile.generates_ncii_or_csam and not profile.ncii_csam_safeguards
    )
    return context


def _matches(predicate: dict[str, Any], context: dict[str, Any]) -> bool:
    """A predicate matches when every key equals (or is a member of) the context."""
    for key, expected in predicate.items():
        actual = context.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def _resolve_tier(context: dict[str, Any], bundle: Bundle) -> RiskTier:
    """Return the first matching tier (rule order in the bundle = precedence)."""
    for rule in bundle.risk_tier_rules:
        if _matches(rule["when"], context):
            return RiskTier(rule["tier"])
    return RiskTier.minimal


def _resolve_obligations(context: dict[str, Any], bundle: Bundle) -> list[AppliedObligation]:
    """Collect every obligation whose rule matches, with conflict detection."""
    catalog = bundle.obligations
    emitted: dict[str, AppliedObligation] = {}
    for rule in bundle.obligation_rules:
        if not _matches(rule["when"], context):
            continue
        oid = rule["obligation"]
        effective_date = date.fromisoformat(rule["effective_date"])
        existing = emitted.get(oid)
        if existing is not None and existing.effective_date != effective_date:
            raise ValueError(
                f"conflicting effective_date for {oid!r}: "
                f"{existing.effective_date} vs {effective_date}"
            )
        meta = catalog[oid]
        emitted[oid] = AppliedObligation(
            id=oid,
            reference=meta["reference"],
            title=meta["title"],
            effective_date=effective_date,
        )
    return list(emitted.values())


def _is_prohibition(oid: str, bundle: Bundle) -> bool:
    """A prohibition obligation is tagged ``category: prohibition`` (or is a known
    legacy id for the frozen pre-category bundle)."""
    entry = bundle.obligations.get(oid, {})
    return entry.get("category") == _PROHIBITION_CATEGORY or oid in _LEGACY_PROHIBITION_IDS


def _apply_prohibited_short_circuit(
    obligations: list[AppliedObligation], bundle: Bundle
) -> list[AppliedObligation]:
    return [o for o in obligations if _is_prohibition(o.id, bundle)]


def _compute_checksum(
    answers: dict[str, Any],
    bundle_sha256: str,
    risk: RiskTier,
    obligations: list[AppliedObligation],
) -> str:
    """Hash over input + bundle identity + RESULT, so it certifies the decision."""
    result = {
        "risk": risk.value,
        "obligations": [
            {"id": o.id, "reference": o.reference, "effective_date": o.effective_date.isoformat()}
            for o in obligations
        ],
    }
    payload = canonical_json({"answers": answers, "bundle_sha256": bundle_sha256, "result": result})
    return sha256_hex(payload)
