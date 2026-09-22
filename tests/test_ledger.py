"""Sealing, saving, loading and verifying a ledger."""

from datetime import UTC, datetime
from pathlib import Path

import pytest

from attestor.ledger import (
    Ledger,
    LedgerError,
    generate_ledger_key,
    load_ledger,
    load_ledger_key,
    public_key_from_hex,
    public_key_hex,
    save_ledger,
    save_ledger_key,
    verify_ledger,
)

AT = datetime(2026, 1, 1, tzinfo=UTC)
DIGEST = "a" * 64


def build(count: int = 3) -> Ledger:
    ledger = Ledger()
    for index in range(count):
        ledger.append(
            id=f"rec-{index}",
            kind="classification",
            subject="sys-1",
            payload_sha256=DIGEST,
            recorded_at=AT,
        )
    return ledger


def test_seal_and_verify_round_trip() -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    result = verify_ledger(ledger.records, root)

    assert result.verified
    assert result.integrity_ok and result.signature_ok
    assert result.timestamp_ok is None
    assert result.detail.startswith("ledger VERIFIED")
    assert "no timestamp" in result.detail


def test_refuses_to_seal_an_empty_ledger() -> None:
    with pytest.raises(LedgerError, match="empty ledger"):
        Ledger().seal(generate_ledger_key())


def test_duplicate_record_id_is_rejected() -> None:
    ledger = build(1)
    with pytest.raises(LedgerError, match="duplicate record id"):
        ledger.append(id="rec-0", kind="k", subject="s", payload_sha256=DIGEST)


def test_editing_a_record_breaks_integrity_but_not_the_signature() -> None:
    """The two axes must fail independently — that is the whole design."""
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)

    tampered = list(ledger.records)
    tampered[0] = tampered[0].model_copy(update={"subject": "sys-9"})
    result = verify_ledger(tampered, root)

    assert result.integrity_ok is False
    assert result.signature_ok is True
    assert result.verified is False
    assert "TAMPERED" in result.detail


def test_rewriting_the_sealed_root_breaks_the_signature() -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    forged = root.model_copy(update={"merkle_root": "b" * 64})

    result = verify_ledger(ledger.records, forged)
    assert result.signature_ok is False


def test_dropping_a_record_is_caught_by_leaf_count() -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    assert verify_ledger(ledger.records[:-1], root).integrity_ok is False


def test_signature_from_a_different_key_does_not_verify() -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    other = root.model_copy(update={"public_key": public_key_hex(generate_ledger_key())})
    assert verify_ledger(ledger.records, other).signature_ok is False


def test_malformed_signature_is_a_failed_verification_not_a_crash() -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    forged = root.model_copy(update={"signature": "zz"})
    assert verify_ledger(ledger.records, forged).signature_ok is False


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    save_ledger(tmp_path / "led", ledger.records, root)

    records, loaded = load_ledger(tmp_path / "led")
    assert [r.model_dump() for r in records] == [r.model_dump() for r in ledger.records]
    assert loaded.merkle_root == root.merkle_root
    assert verify_ledger(records, loaded).verified


def test_load_rejects_a_records_file_that_is_not_an_array(tmp_path: Path) -> None:
    ledger = build()
    root = ledger.seal(generate_ledger_key(), sealed_at=AT)
    save_ledger(tmp_path, ledger.records, root)
    (tmp_path / "records.json").write_text("{}", encoding="utf-8")

    with pytest.raises(LedgerError, match="must contain a JSON array"):
        load_ledger(tmp_path)


def test_key_pem_round_trip(tmp_path: Path) -> None:
    key = generate_ledger_key()
    path = save_ledger_key(key, tmp_path / "k" / "key.pem")
    assert public_key_hex(load_ledger_key(path)) == public_key_hex(key)


def test_public_key_hex_round_trip() -> None:
    key = generate_ledger_key()
    rebuilt = public_key_from_hex(public_key_hex(key))
    assert public_key_hex(rebuilt) == public_key_hex(key)


@pytest.mark.parametrize("value", ["nothex", "ab"])
def test_public_key_from_hex_rejects_bad_input(value: str) -> None:
    with pytest.raises(ValueError):
        public_key_from_hex(value)


def test_loading_a_non_ed25519_key_is_rejected(tmp_path: Path) -> None:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec

    path = tmp_path / "ec.pem"
    path.write_bytes(
        ec.generate_private_key(ec.SECP256R1()).private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    with pytest.raises(ValueError, match="not an Ed25519 private key"):
        load_ledger_key(path)
