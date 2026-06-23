"""Offline verification with public inputs only — and tamper detection."""

from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.ledger import (
    build_timestamp_info,
    prove_inclusion,
    public_key_hex,
    seal,
    verify_inclusion_proof,
    verify_ledger,
)

# Fixed test key (deterministic seed) — a throwaway, NEVER a real secret.
_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
_RECORDS = [
    {"type": "dossier", "id": "sys-1", "sha256": "aa"},
    {"type": "c2pa", "id": "img-1", "sha256": "bb"},
    {"type": "dossier", "id": "sys-2", "sha256": "cc"},
]
_FIXTURES = Path(__file__).parent / "fixtures" / "ledger"


def _tsa_certs() -> tuple[x509.Certificate, x509.Certificate]:
    leaf = x509.load_pem_x509_certificate((_FIXTURES / "tsa" / "leaf.pem").read_bytes())
    root = x509.load_pem_x509_certificate((_FIXTURES / "tsa" / "root.pem").read_bytes())
    return leaf, root


def test_valid_ledger_verifies_with_public_inputs_only() -> None:
    # seal() uses the operator's key; verify_ledger() touches only public artifacts.
    signed = seal(_RECORDS, _TEST_KEY)
    result = verify_ledger(_RECORDS, signed)

    assert result.integrity_ok is True
    assert result.signature_ok is True
    assert result.verified is True
    assert result.has_timestamp is False


def test_tampered_record_fails_integrity() -> None:
    signed = seal(_RECORDS, _TEST_KEY)
    tampered = [dict(r) for r in _RECORDS]
    tampered[1]["sha256"] = "ff"  # alter one record after sealing

    result = verify_ledger(tampered, signed)
    assert result.integrity_ok is False
    assert result.verified is False


def test_dropped_record_fails_integrity() -> None:
    signed = seal(_RECORDS, _TEST_KEY)
    result = verify_ledger(_RECORDS[:2], signed)  # leaf_count mismatch
    assert result.integrity_ok is False
    assert result.verified is False


def test_tampered_signature_fails() -> None:
    signed = seal(_RECORDS, _TEST_KEY).model_copy(update={"signature": "00" * 64})
    result = verify_ledger(_RECORDS, signed)
    assert result.signature_ok is False
    assert result.verified is False


def test_wrong_public_key_fails_signature() -> None:
    other = Ed25519PrivateKey.from_private_bytes(bytes([7]) * 32)
    signed = seal(_RECORDS, _TEST_KEY).model_copy(
        update={"public_key": public_key_hex(other.public_key())}
    )
    result = verify_ledger(_RECORDS, signed)
    assert result.signature_ok is False


def test_forged_root_fails_both_axes() -> None:
    signed = seal(_RECORDS, _TEST_KEY).model_copy(update={"merkle_root": "00" * 32})
    result = verify_ledger(_RECORDS, signed)
    assert result.integrity_ok is False  # recomputed root != forged root
    assert result.signature_ok is False  # signature was over the real root commitment


def test_valid_ledger_with_untrusted_tsa_is_still_verified() -> None:
    # The F5 lesson: a valid token from an unrecognised TSA is NOT "tampered".
    token = (_FIXTURES / "timestamp.tsr").read_bytes()
    signed = seal(_RECORDS, _TEST_KEY).model_copy(update={"timestamp": build_timestamp_info(token)})
    leaf, root = _tsa_certs()

    result = verify_ledger(_RECORDS, signed, tsa_leaf=leaf, tsa_root=root)
    assert result.verified is True  # integrity + signature hold
    assert result.has_timestamp is True
    assert result.timestamp_ok is True  # token is cryptographically valid
    assert result.tsa_trusted is False  # ...but the TSA is not a recognised authority
    assert "UNTRUSTED" in result.headline


def test_inclusion_proof_verifies_and_binds_record() -> None:
    proof = prove_inclusion(_RECORDS, 1)
    assert verify_inclusion_proof(proof) is True
    assert verify_inclusion_proof(proof, record=_RECORDS[1]) is True
    # A different record does not match the proof's leaf hash.
    assert verify_inclusion_proof(proof, record={"type": "forged"}) is False
