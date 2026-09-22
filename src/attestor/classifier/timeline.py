"""Dual-scenario timeline: the same profile under two bundles, side by side.

The value of this view is showing BOTH timelines honestly. It used to contrast the
binding legal text with a *provisional* Omnibus; since Regulation (EU) 2026/1744
entered into force on 2026-07-27 it contrasts the Regulation **as originally
enacted** with the Regulation **as it binds today**. Knowing what changed, and when,
is part of the answer a compliance owner needs.

That this module survived the Omnibus becoming law with a constant change and no new
logic is the point of the design: the caveat is read from the binding bundle's own
``meta.status_note`` — a single source of truth — and never hardcoded here,
because the status is precisely the thing that changes.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict

from attestor.classifier.bundle import Bundle, load_bundle
from attestor.classifier.engine import classify
from attestor.classifier.model import RiskTier, SystemProfile

BINDING_SCENARIO = "in-force"
LEGAL_TEXT_VERSION = "v2026-08"
# The Omnibus as modelled on 2026-06-23, while it was still a proposal. Kept for
# comparison; it is no longer what binds.
OMNIBUS_VERSION = "omnibus-2026"
IN_FORCE_VERSION = "reg-2026-1744"


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
    """One profile under the Regulation as enacted and as it binds today."""

    model_config = ConfigDict(frozen=True)

    binding_scenario: str
    legal_text_risk: RiskTier
    omnibus_risk: RiskTier
    # Status note of the bundle that BINDS, read from its ``meta``. The field keeps the
    # name ``omnibus_status`` so the API and the dashboard do not break; what it carries
    # is now the in-force note rather than the provisional one.
    omnibus_status: str
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
    """Classify ``profile`` under both scenarios and return the per-obligation deltas.

    The second bundle defaults to the one in force. Pass ``omnibus_bundle`` explicitly to
    compare against the frozen provisional overlay instead.
    """
    legal_bundle = legal_bundle or load_bundle(LEGAL_TEXT_VERSION)
    omnibus_bundle = omnibus_bundle or load_bundle(IN_FORCE_VERSION)

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
