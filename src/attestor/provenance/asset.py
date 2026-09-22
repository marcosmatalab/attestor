"""A deterministic, dependency-free PNG, so the demo has something to sign.

Written by hand rather than with an imaging library for one reason: the demo has
to produce the *same bytes* on every machine. A generated PNG whose encoder
version can change would make the C2PA digest move for reasons that have nothing
to do with the engine, and "the same input yields the same output" is the claim
this repo is built on.
"""

import struct
import zlib


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))


def synthetic_png(
    width: int = 64, height: int = 64, rgb: tuple[int, int, int] = (32, 80, 140)
) -> bytes:
    """Return a solid-colour RGB PNG of ``width`` x ``height``, byte-for-byte stable."""
    if width < 1 or height < 1:
        raise ValueError("PNG dimensions must be positive")
    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + bytes(rgb) * width  # filter byte 0 (None) + RGB triples
    # level=9 and a fixed input make the compressed stream deterministic.
    data = zlib.compress(row * height, 9)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", header)
        + _chunk(b"IDAT", data)
        + _chunk(b"IEND", b"")
    )
