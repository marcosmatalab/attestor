"""RFC3161 trusted timestamping, as a pure codec — no I/O.

This module builds a ``TimeStampReq`` and parses a ``TimeStampResp``; it never
opens a socket. That is deliberate and it is the reason the invariant "the engine
does no network" is literally true and testable (``tests/test_architecture.py``).
Fetching the token over HTTP is the caller's job, at the edge.

What is verified here, precisely: that the token's ``messageImprint`` is the
digest of the signed root, i.e. that *this* token timestamps *this* ledger and
not some other document. That is the binding an attacker would have to break to
back-date evidence.

What is NOT verified here, and is a documented simplification: the TSA's CMS
signature and its certificate chain. A full AdES "T" validation needs a CMS
verifier and a TSA trust list, neither of which ships in this repo. So a token is
reported as *bound*, never as *trusted* — the same integrity/trust split the C2PA
verifier uses, for the same reason.
"""

import hashlib
from datetime import UTC, datetime

from attestor.ledger.model import RecordTimestamp, SignedRoot

# id-ct-TSTInfo, RFC 3161 s2.4.2
_TST_INFO_OID = bytes.fromhex("06 0b 2a 86 48 86 f7 0d 01 09 10 01 04".replace(" ", ""))
# id-sha256, RFC 5754
_SHA256_OID_DER = bytes.fromhex("06 09 60 86 48 01 65 03 04 02 01".replace(" ", ""))

_TAG_INTEGER = 0x02
_TAG_OCTET_STRING = 0x04
_TAG_OID = 0x06
_TAG_GENERALIZED_TIME = 0x18
_TAG_SEQUENCE = 0x30


class TimestampError(ValueError):
    """Raised when an RFC3161 token cannot be parsed or does not bind."""


def _encode_length(length: int) -> bytes:
    if length < 0x80:
        return bytes([length])
    body = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def _encode(tag: int, body: bytes) -> bytes:
    return bytes([tag]) + _encode_length(len(body)) + body


def build_timestamp_request(digest: bytes, *, cert_req: bool = True) -> bytes:
    """Build a DER ``TimeStampReq`` asking a TSA to timestamp ``digest`` (SHA-256)."""
    if len(digest) != 32:
        raise TimestampError(f"SHA-256 digest must be 32 bytes, got {len(digest)}")
    algorithm = _encode(_TAG_SEQUENCE, _SHA256_OID_DER + _encode(0x05, b""))
    message_imprint = _encode(_TAG_SEQUENCE, algorithm + _encode(_TAG_OCTET_STRING, digest))
    version = _encode(_TAG_INTEGER, b"\x01")
    cert_req_der = _encode(0x01, b"\xff" if cert_req else b"\x00")
    return _encode(_TAG_SEQUENCE, version + message_imprint + cert_req_der)


def _read_tlv(data: bytes, offset: int) -> tuple[int, int, int]:
    """Return ``(tag, body_start, body_end)`` for the TLV at ``offset``."""
    if offset + 2 > len(data):
        raise TimestampError("truncated DER: no room for tag and length")
    tag = data[offset]
    length_byte = data[offset + 1]
    cursor = offset + 2
    if length_byte < 0x80:
        length = length_byte
    else:
        count = length_byte & 0x7F
        if count == 0 or cursor + count > len(data):
            raise TimestampError("truncated DER: bad long-form length")
        length = int.from_bytes(data[cursor : cursor + count], "big")
        cursor += count
    end = cursor + length
    if end > len(data):
        raise TimestampError("truncated DER: declared length exceeds the buffer")
    return tag, cursor, end


def _extract_tst_info(tsr: bytes) -> bytes:
    """Pull the DER-encoded ``TSTInfo`` out of a ``TimeStampResp``.

    The token is CMS ``SignedData``; rather than implement CMS, we locate the
    ``id-ct-TSTInfo`` content-type OID and take the OCTET STRING that follows it,
    which is where RFC 3161 puts the encapsulated content.
    """
    index = tsr.find(_TST_INFO_OID)
    if index < 0:
        raise TimestampError("not an RFC3161 token: id-ct-TSTInfo content type not found")
    cursor = index + len(_TST_INFO_OID)
    # Walk forward over the explicit [0] wrapper(s) to the OCTET STRING payload.
    while cursor < len(tsr):
        tag, start, end = _read_tlv(tsr, cursor)
        if tag == _TAG_OCTET_STRING:
            return tsr[start:end]
        if tag & 0x20:  # constructed: descend
            cursor = start
            continue
        cursor = end
    raise TimestampError("malformed RFC3161 token: no TSTInfo content octets")


def _parse_generalized_time(raw: bytes) -> datetime:
    text = raw.decode("ascii")
    if not text.endswith("Z"):
        raise TimestampError(f"genTime is not UTC: {text!r}")
    stem, _, fraction = text[:-1].partition(".")
    parsed = datetime.strptime(stem, "%Y%m%d%H%M%S").replace(tzinfo=UTC)
    if fraction:
        micros = int(fraction.ljust(6, "0")[:6])
        parsed = parsed.replace(microsecond=micros)
    return parsed


def parse_timestamp(tsr: bytes) -> RecordTimestamp:
    """Parse a DER ``TimeStampResp`` into a ``RecordTimestamp``."""
    info = _extract_tst_info(tsr)
    tag, start, end = _read_tlv(info, 0)
    if tag != _TAG_SEQUENCE:
        raise TimestampError("malformed TSTInfo: expected a SEQUENCE")

    cursor = start
    fields: list[tuple[int, int, int]] = []
    while cursor < end:
        field = _read_tlv(info, cursor)
        fields.append(field)
        cursor = field[2]

    # TSTInfo ::= SEQUENCE { version, policy, messageImprint, serialNumber, genTime, ... }
    if len(fields) < 5:
        raise TimestampError(f"malformed TSTInfo: expected >= 5 fields, got {len(fields)}")

    policy_tag, policy_start, policy_end = fields[1]
    policy = _oid_to_dotted(info[policy_start:policy_end]) if policy_tag == _TAG_OID else None

    imprint_tag, imprint_start, imprint_end = fields[2]
    if imprint_tag != _TAG_SEQUENCE:
        raise TimestampError("malformed TSTInfo: messageImprint is not a SEQUENCE")
    algorithm = _read_tlv(info, imprint_start)
    hashed_tag, hashed_start, hashed_end = _read_tlv(info, algorithm[2])
    if hashed_tag != _TAG_OCTET_STRING or hashed_end > imprint_end:
        raise TimestampError("malformed TSTInfo: hashedMessage is not an OCTET STRING")
    imprint = info[hashed_start:hashed_end].hex()

    time_tag, time_start, time_end = fields[4]
    if time_tag != _TAG_GENERALIZED_TIME:
        raise TimestampError("malformed TSTInfo: genTime is not a GeneralizedTime")

    return RecordTimestamp(
        tsr_sha256=hashlib.sha256(tsr).hexdigest(),
        gen_time=_parse_generalized_time(info[time_start:time_end]),
        message_imprint=imprint,
        policy=policy,
    )


def _oid_to_dotted(body: bytes) -> str:
    if not body:
        return ""
    first = body[0]
    arcs = [str(first // 40), str(first % 40)]
    value = 0
    for byte in body[1:]:
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            arcs.append(str(value))
            value = 0
    return ".".join(arcs)


def root_digest(root: SignedRoot) -> bytes:
    """The SHA-256 digest a TSA is asked to timestamp for ``root``."""
    return hashlib.sha256(root.signed_payload()).digest()


def timestamp_binds(root: SignedRoot, stamp: RecordTimestamp) -> bool:
    """True when ``stamp`` attests to *this* root and not another document."""
    return stamp.message_imprint.lower() == root_digest(root).hex()
