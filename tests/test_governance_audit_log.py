"""Tests for the Art. 12 tamper-evident audit log (anchored in the F6 ledger)."""

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.governance import Art12Event, Art12EventType, Art12Log, verify_log

# Fixed test key (deterministic seed) — a throwaway, NEVER a real secret.
_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))


def _populated_log() -> Art12Log:
    log = Art12Log()
    log.record(
        Art12Event(
            event_type=Art12EventType.risk_situation,
            occurred_at="2026-08-03T10:00:00+00:00",
            detail={"description": "input distribution shift detected"},
        )
    )
    log.record(
        Art12Event(
            event_type=Art12EventType.operation_monitoring,
            occurred_at="2026-08-03T10:05:00+00:00",
            detail={"throughput": 42},
        )
    )
    # Art. 12(3): minimum logging for Annex III(1)(a) biometric identification.
    log.record(
        Art12Event(
            event_type=Art12EventType.biometric_use,
            occurred_at="2026-08-03T10:10:00+00:00",
            detail={
                "period_start": "2026-08-03T10:10:00+00:00",
                "period_end": "2026-08-03T10:10:30+00:00",
                "reference_database": "watchlist-v7",
                "matched_input": "probe-0x9f",
                "verifier": "operator-17",
            },
        )
    )
    return log


def test_log_is_append_only_and_ordered() -> None:
    log = Art12Log()
    first = log.record(Art12Event(event_type=Art12EventType.risk_situation, occurred_at="t0"))
    second = log.record(
        Art12Event(event_type=Art12EventType.post_market_monitoring, occurred_at="t1")
    )
    assert (first, second) == (0, 1)
    assert [e.event_type for e in log.events] == [
        Art12EventType.risk_situation,
        Art12EventType.post_market_monitoring,
    ]


def test_sealed_log_verifies_offline() -> None:
    log = _populated_log()
    signed = log.seal(_TEST_KEY)

    result = verify_log(log.records, signed)
    assert result.verified is True
    assert result.integrity_ok is True
    assert result.signature_ok is True


def test_tampering_with_an_event_breaks_verification() -> None:
    log = _populated_log()
    signed = log.seal(_TEST_KEY)

    tampered = [dict(r) for r in log.records]
    tampered[0]["detail"] = {"description": "nothing to see here"}

    result = verify_log(tampered, signed)
    assert result.integrity_ok is False  # tamper-evident
    assert result.verified is False


def test_biometric_event_carries_art12_3_fields() -> None:
    log = _populated_log()
    biometric = next(e for e in log.events if e.event_type is Art12EventType.biometric_use)
    for field in ("period_start", "period_end", "reference_database", "matched_input", "verifier"):
        assert field in biometric.detail


def test_seal_is_deterministic() -> None:
    # Same events + same key -> same Merkle root and same signature.
    assert _populated_log().seal(_TEST_KEY) == _populated_log().seal(_TEST_KEY)
