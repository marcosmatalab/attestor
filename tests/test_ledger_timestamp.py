"""Offline verification of an RFC 3161 timestamp over the signed root.

Uses a RECORDED freeTSA token (minted once, committed as a fixture) over the
deterministic signature of a fixed test ledger. CI runs fully offline: no network is
touched here. The token is not byte-reproducible, so there is no byte-identity test —
we verify the token cryptographically and check it binds our signature.
"""

import hashlib
from pathlib import Path

import rfc3161_client as tsp
from cryptography import x509
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.ledger import build_timestamp_info, seal, verify_timestamp

# The fixed test ledger the committed token was minted over (see the mint step).
_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
_RECORDS = [
    {"type": "dossier", "id": "sys-1", "sha256": "aa"},
    {"type": "c2pa", "id": "img-1", "sha256": "bb"},
    {"type": "dossier", "id": "sys-2", "sha256": "cc"},
]
_FIXTURES = Path(__file__).parent / "fixtures" / "ledger"


def _signature() -> bytes:
    return bytes.fromhex(seal(_RECORDS, _TEST_KEY).signature)


def _token() -> bytes:
    return (_FIXTURES / "timestamp.tsr").read_bytes()


def _tsa_certs() -> tuple[x509.Certificate, x509.Certificate]:
    leaf = x509.load_pem_x509_certificate((_FIXTURES / "tsa" / "leaf.pem").read_bytes())
    root = x509.load_pem_x509_certificate((_FIXTURES / "tsa" / "root.pem").read_bytes())
    return leaf, root


def test_token_verifies_offline_and_binds_the_signature() -> None:
    leaf, root = _tsa_certs()
    ok, gen_time = verify_timestamp(_token(), _signature(), tsa_leaf=leaf, tsa_root=root)
    assert ok is True
    assert gen_time is not None


def test_token_imprint_is_sha256_of_the_signature() -> None:
    decoded = tsp.decode_timestamp_response(_token())
    assert decoded.tst_info.message_imprint.message == hashlib.sha256(_signature()).digest()


def test_token_rejects_a_different_message() -> None:
    leaf, root = _tsa_certs()
    # A token bound to our signature must NOT verify against different bytes.
    ok, _ = verify_timestamp(_token(), b"some other root signature", tsa_leaf=leaf, tsa_root=root)
    assert ok is False


def test_build_timestamp_info_extracts_gen_time() -> None:
    info = build_timestamp_info(_token())
    assert info.gen_time is not None
    assert info.token_b64  # the authoritative artifact is carried as base64
