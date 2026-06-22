"""Tests for the canonical JSON / hashing primitive."""

import math

import pytest

from attestor.canonical import canonical_json, sha256_hex


def test_key_order_does_not_change_output() -> None:
    a = canonical_json({"b": 1, "a": 2, "c": 3})
    b = canonical_json({"c": 3, "a": 2, "b": 1})
    assert a == b


def test_no_insignificant_whitespace() -> None:
    assert canonical_json({"a": 1, "b": [1, 2]}) == b'{"a":1,"b":[1,2]}'


def test_non_ascii_is_preserved_as_utf8() -> None:
    # "café" -> the e-acute is UTF-8 0xC3 0xA9, not an \u escape.
    assert canonical_json({"k": "café"}) == b'{"k":"caf\xc3\xa9"}'


def test_nan_is_rejected() -> None:
    with pytest.raises(ValueError):
        canonical_json({"x": math.nan})


def test_infinity_is_rejected() -> None:
    with pytest.raises(ValueError):
        canonical_json({"x": math.inf})


def test_sha256_hex_known_vector() -> None:
    # SHA-256 of the empty byte string.
    assert sha256_hex(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_hex_is_stable() -> None:
    payload = canonical_json({"hello": "world"})
    assert sha256_hex(payload) == sha256_hex(payload)
