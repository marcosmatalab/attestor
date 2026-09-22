"""RFC3161 codec: built requests, parsed tokens, and the binding check.

The fixture ``timestamp.tsr`` is a **real** response from a public TSA
(freetsa.org), captured once. Testing the parser against a genuine token rather
than one this repo also wrote is the only way the test says anything: a
round-trip against our own encoder would pass even if the encoder were wrong.
"""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

from attestor.ledger import Ledger, generate_ledger_key, root_digest, timestamp_binds
from attestor.ledger.ledger import attach_timestamp
from attestor.ledger.timestamp import (
    TimestampError,
    build_timestamp_request,
    parse_timestamp,
)
from attestor.ledger.verifier import verify_ledger

FIXTURE = Path(__file__).parent / "fixtures" / "ledger" / "timestamp.tsr"
# The digest the fixture token was requested over.
FIXTURE_IMPRINT = hashlib.sha256(b"attestor-ledger-root-fixture").hexdigest()
AT = datetime(2026, 1, 1, tzinfo=UTC)


def a_ledger() -> Ledger:
    ledger = Ledger()
    ledger.append(
        id="rec-1", kind="classification", subject="sys-1", payload_sha256="a" * 64, recorded_at=AT
    )
    return ledger


def test_request_is_well_formed_der() -> None:
    request = build_timestamp_request(hashlib.sha256(b"x").digest())
    assert request[0] == 0x30  # SEQUENCE
    assert len(request) - 2 == request[1]  # short-form length covers the body
    assert hashlib.sha256(b"x").digest() in request


def test_request_rejects_a_non_sha256_digest() -> None:
    with pytest.raises(TimestampError, match="32 bytes"):
        build_timestamp_request(b"short")


def test_parses_a_real_tsa_response() -> None:
    stamp = parse_timestamp(FIXTURE.read_bytes())

    assert stamp.message_imprint == FIXTURE_IMPRINT
    assert stamp.gen_time.tzinfo is not None
    assert stamp.gen_time.year >= 2026
    assert stamp.policy  # a TSA always states its policy OID
    assert stamp.tsr_sha256 == hashlib.sha256(FIXTURE.read_bytes()).hexdigest()


def test_parsing_a_non_token_is_an_error() -> None:
    with pytest.raises(TimestampError, match="id-ct-TSTInfo"):
        parse_timestamp(b"not a timestamp response")


def test_truncated_token_is_an_error() -> None:
    """Cut inside the encapsulated TSTInfo, where the length prefix stops being honest."""
    data = FIXTURE.read_bytes()
    tst_info_oid = bytes.fromhex("060b2a864886f70d01091001" + "04")
    cut = data.find(tst_info_oid) + len(tst_info_oid) + 20

    with pytest.raises(TimestampError, match="truncated DER"):
        parse_timestamp(data[:cut])


def test_a_token_for_another_document_does_not_bind() -> None:
    """The check that stops a valid token being reused to back-date other evidence."""
    root = a_ledger().seal(generate_ledger_key(), sealed_at=AT)
    stamp = parse_timestamp(FIXTURE.read_bytes())

    assert timestamp_binds(root, stamp) is False

    stamped = attach_timestamp(root, stamp)
    result = verify_ledger(a_ledger().records, stamped)
    assert result.timestamp_ok is False
    assert result.verified is False
    assert "does NOT bind" in result.detail


def test_a_token_over_this_root_binds() -> None:
    ledger = a_ledger()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    stamp = parse_timestamp(FIXTURE.read_bytes()).model_copy(
        update={"message_imprint": root_digest(root).hex()}
    )

    stamped = attach_timestamp(root, stamp)
    result = verify_ledger(ledger.records, stamped)
    assert result.timestamp_ok is True
    assert result.verified is True
    assert "binding only, not TSA trust" in result.detail
