"""Deterministic EU AI Act risk classifier.

The classification *decision* is a rule engine over a versioned regulatory bundle
— no LLM — so the same input and bundle always produce the same output, with a
content-addressed checksum an auditor can reproduce.
"""

from attestor.classifier.bundle import Bundle, load_bundle
from attestor.classifier.engine import classify
from attestor.classifier.model import (
    AnnexIIIArea,
    AppliedObligation,
    Classification,
    ContentLifecycle,
    DeployerType,
    ProhibitedPractice,
    RiskTier,
    Role,
    SystemProfile,
)
from attestor.classifier.timeline import (
    ObligationTimeline,
    TimelineComparison,
    compare_timelines,
)

__all__ = [
    "AnnexIIIArea",
    "AppliedObligation",
    "Bundle",
    "Classification",
    "ContentLifecycle",
    "DeployerType",
    "ObligationTimeline",
    "ProhibitedPractice",
    "RiskTier",
    "Role",
    "SystemProfile",
    "TimelineComparison",
    "classify",
    "compare_timelines",
    "load_bundle",
]
