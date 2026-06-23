"""Optional RFC 3161 timestamping of the signed root (an existence-in-time proof).

REQUESTING a token needs network and an ``RFC3161_TSA_URL`` (opt-in). VERIFYING a token
is fully offline: the token is a CMS ``SignedData``; given the TSA's certificate(s) as
out-of-band trust anchors, both the signature and the message imprint are checked with no
network and no private key. Trust in the TSA itself — is it a *recognised* authority? —
is a SEPARATE axis (``tsa_trusted`` in the verifier), mirroring C2PA signer trust in F5:
a free/dev TSA can issue a perfectly valid token yet not be a recognised authority.

The timestamp covers the 64-byte Ed25519 signature, so the chain is
token -> signature -> Merkle root -> records.
"""

import base64
import hashlib
import urllib.request

import rfc3161_client as tsp
from cryptography import x509

from attestor.ledger.model import TimestampInfo

# RFC 3161 PKIStatus values that mean a token was issued.
_GRANTED = (0, 1)  # granted, grantedWithMods
_TIMESTAMP_QUERY = "application/timestamp-query"


def request_timestamp(message: bytes, tsa_url: str, *, timeout: int = 30) -> bytes:
    """Request an RFC 3161 token over ``message`` from ``tsa_url`` (network, opt-in)."""
    request = (
        tsp.TimestampRequestBuilder()
        .data(message)
        .hash_algorithm(tsp.HashAlgorithm.SHA256)
        .cert_request()
        .build()
    )
    http_request = urllib.request.Request(
        tsa_url, data=request.as_bytes(), headers={"Content-Type": _TIMESTAMP_QUERY}
    )
    with urllib.request.urlopen(http_request, timeout=timeout) as response:
        token_bytes = response.read()
    decoded = tsp.decode_timestamp_response(token_bytes)
    if int(decoded.status) not in _GRANTED:
        raise ValueError(f"TSA did not grant the timestamp (status {decoded.status})")
    return token_bytes


def build_timestamp_info(token_bytes: bytes) -> TimestampInfo:
    """Summarise a token into the publishable :class:`TimestampInfo` (token + gen_time)."""
    info = tsp.decode_timestamp_response(token_bytes).tst_info
    return TimestampInfo(
        token_b64=base64.b64encode(token_bytes).decode("ascii"),
        tsa_name=str(info.name) if info.name is not None else None,
        gen_time=info.gen_time.isoformat(),
    )


def verify_timestamp(
    token_bytes: bytes,
    message: bytes,
    *,
    tsa_leaf: x509.Certificate,
    tsa_root: x509.Certificate,
) -> tuple[bool, str | None]:
    """Verify, OFFLINE, that the token is valid and binds ``message``.

    Returns ``(timestamp_ok, gen_time_iso)``. ``timestamp_ok`` means the CMS signature
    verifies against the provided TSA certificates AND the token's imprint is
    ``sha256(message)``. Whether the TSA is a *recognised* authority is decided
    separately by the caller (``tsa_trusted``). No network is used.
    """
    decoded = tsp.decode_timestamp_response(token_bytes)
    gen_time = decoded.tst_info.gen_time.isoformat()
    # Binding: the imprint must be sha256 of our signed-root signature.
    if decoded.tst_info.message_imprint.message != hashlib.sha256(message).digest():
        return False, gen_time
    try:
        verifier = (
            tsp.VerifierBuilder().tsa_certificate(tsa_leaf).add_root_certificate(tsa_root).build()
        )
        verifier.verify_message(decoded, message)
    except Exception:
        return False, gen_time
    return True, gen_time
