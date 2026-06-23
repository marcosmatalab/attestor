"""Dual-scenario timeline: the same profile under both bundles, side by side.

The value of F2 is showing BOTH timelines honestly — not replacing the binding
legal text with the Omnibus. ``compare_timelines`` classifies one profile under
the legal-text bundle (the binding default) and the provisional Omnibus bundle,
then reports, per obligation, the legal-text date vs the Omnibus date.

The provisional caveat is read from the Omnibus bundle's own ``meta.status_note``
— a single source of truth — never hardcoded here (the adoption status changes).
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from attestor.classifier.bundle import Bundle, load_bundle
from attestor.classifier.engine import classify
from attestor.classifier.model import RiskTier, SystemProfile

BINDING_SCENARIO = "legal-text"
LEGAL_TEXT_VERSION = "v2026-08"
OMNIBUS_VERSION = "omnibus-2026"


class ObligationTimeline(BaseModel):
    """One obligation's effective date under each scenario (``None`` = not applicable)."""

    model_config = ConfigDict(frozen=True)

    id: str
    reference: str
    title: str
    legal_text_date: date | None
    omnibus_date: date | None

    @property
    def diverges(self) -> bool:
        return self.legal_text_date != self.omnibus_date


class TimelineComparison(BaseModel):
    """The legal-text vs Omnibus comparison for one profile."""

    model_config = ConfigDict(frozen=True)

    binding_scenario: str
    legal_text_risk: RiskTier
    omnibus_risk: RiskTier
    omnibus_status: str  # provisional caveat, read from the Omnibus bundle meta
    obligations: tuple[ObligationTimeline, ...]

    @property
    def risk_diverges(self) -> bool:
        return self.legal_text_risk != self.omnibus_risk

    @property
    def divergences(self) -> tuple[ObligationTimeline, ...]:
        return tuple(o for o in self.obligations if o.diverges)


def compare_timelines(
    profile: SystemProfile,
    *,
    legal_bundle: Bundle | None = None,
    omnibus_bundle: Bundle | None = None,
) -> TimelineComparison:
    """Classify ``profile`` under both scenarios and return the per-obligation deltas."""
    legal_bundle = legal_bundle or load_bundle(LEGAL_TEXT_VERSION)
    omnibus_bundle = omnibus_bundle or load_bundle(OMNIBUS_VERSION)

    legal = classify(profile, legal_bundle)
    omnibus = classify(profile, omnibus_bundle)

    legal_by_id = {o.id: o for o in legal.obligations}
    omnibus_by_id = {o.id: o for o in omnibus.obligations}

    rows: list[ObligationTimeline] = []
    for oid in sorted(legal_by_id.keys() | omnibus_by_id.keys()):
        descriptor = legal_by_id.get(oid) or omnibus_by_id[oid]
        legal_obl = legal_by_id.get(oid)
        omnibus_obl = omnibus_by_id.get(oid)
        rows.append(
            ObligationTimeline(
                id=oid,
                reference=descriptor.reference,
                title=descriptor.title,
                legal_text_date=legal_obl.effective_date if legal_obl else None,
                omnibus_date=omnibus_obl.effective_date if omnibus_obl else None,
            )
        )

    return TimelineComparison(
        binding_scenario=BINDING_SCENARIO,
        legal_text_risk=legal.risk,
        omnibus_risk=omnibus.risk,
        omnibus_status=str(omnibus_bundle.meta.get("status_note", "")).strip(),
        obligations=tuple(rows),
    )
