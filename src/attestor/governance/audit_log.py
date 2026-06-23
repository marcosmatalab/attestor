"""Art. 12 logging capability, anchored in the append-only ledger (F6).

Article 12 requires high-risk AI systems to automatically record events over their
lifetime. This provides a typed event model for the events Art. 12(2)/(3) point to and
records them as records in the F6 ledger, so the log is **tamper-evident** and
**offline-verifiable** (Merkle root + Ed25519 signature, optionally RFC 3161). The event
types map to Art. 12(2): risk situations (a), post-market monitoring (b, Art. 72), and
operation monitoring (c, Art. 26(5)); plus the Art. 12(3) minimum for Annex III(1)(a)
biometric identification (period of each use, reference database, matched input data, and
the persons who verified the result — carried in the event ``detail``).

HONESTY: this is a logging CAPABILITY. It is necessary but NOT sufficient for Art. 12
conformity — recording events here does not, on its own, make a system compliant. There
is no clock: the caller supplies each event's timestamp, so the log stays deterministic.
"""

from enum import StrEnum
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pydantic import BaseModel, ConfigDict

from attestor.ledger import Ledger, LedgerVerification, SignedRoot, verify_ledger

ART12_DISCLAIMER = (
    "An Art. 12 logging CAPABILITY: it records the event types Art. 12(2)/(3) point to "
    "and anchors them in the append-only ledger so the log is tamper-evident and "
    "offline-verifiable. The capability is necessary but NOT sufficient for Art. 12 "
    "conformity; recording events here does not by itself make a system compliant."
)


class Art12EventType(StrEnum):
    """Event categories Art. 12(2)/(3) require a high-risk AI system to log."""

    risk_situation = "risk_situation"  # 12(2)(a): may present a risk / substantial modification
    post_market_monitoring = "post_market_monitoring"  # 12(2)(b): Art. 72
    operation_monitoring = "operation_monitoring"  # 12(2)(c): Art. 26(5)
    biometric_use = "biometric_use"  # 12(3): Annex III(1)(a) minimum logging


class Art12Event(BaseModel):
    """One logged event. ``detail`` carries the structured payload (e.g. the Art. 12(3)
    biometric fields: period_start, period_end, reference_database, matched_input, verifier)."""

    model_config = ConfigDict(frozen=True)

    event_type: Art12EventType
    occurred_at: str  # ISO 8601, supplied by the caller (the module has no clock)
    detail: dict[str, Any] = {}


class Art12Log:
    """An append-only Art. 12 event log, sealable into a tamper-evident signed root."""

    def __init__(self) -> None:
        self._events: list[Art12Event] = []
        self._ledger = Ledger()

    def record(self, event: Art12Event) -> int:
        """Append an event and return its index. Append-only: events are never reordered."""
        self._events.append(event)
        return self._ledger.append(event.model_dump(mode="json"))

    @property
    def events(self) -> list[Art12Event]:
        return list(self._events)

    @property
    def records(self) -> list[dict[str, Any]]:
        """The ledger records (public artifacts for offline verification)."""
        return self._ledger.records

    def seal(self, private_key: Ed25519PrivateKey) -> SignedRoot:
        """Seal the log into an Ed25519-signed Merkle root (reuses the F6 ledger)."""
        return self._ledger.seal(private_key)


def verify_log(records: list[dict[str, Any]], signed_root: SignedRoot) -> LedgerVerification:
    """Verify a sealed Art. 12 log offline (delegates to the F6 ledger verifier)."""
    return verify_ledger(records, signed_root)
