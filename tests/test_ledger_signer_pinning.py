"""Pinning the signer: a re-sealed ledger must not pass as the original.

The signature in ``signed_root.json`` is checked with the public key stored in the same
file. On its own that only proves the records match *some* key: whoever edits the
records and re-seals them with a fresh key gets a valid signature. The pin closes that
gap - ``--public-key`` names the key the verifier expects, and a ledger signed by any
other key is reported as ``UNTRUSTED SIGNER`` (exit 3), never as ``VERIFIED``.
"""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.canonical import canonical_json
from attestor.cli import main as cli_main
from attestor.ledger import load_ledger, save_ledger, seal, verify_ledger
from attestor.ledger.__main__ import main as module_main
from attestor.ledger.keys import load_pinned_public_key, public_key_fingerprint

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "ledger"
EXAMPLE_KEY = EXAMPLE / "public_key.pem"

EXIT_OK, EXIT_TAMPERED, EXIT_USAGE, EXIT_UNTRUSTED_SIGNER = 0, 1, 2, 3


def _copy_example(target: Path) -> Path:
    for name in ("records.json", "signed_root.json"):
        shutil.copy(EXAMPLE / name, target / name)
    return target


def _forge(target: Path) -> Path:
    """The attack: edit a record, then re-seal everything with a key the attacker owns."""
    records, _ = load_ledger(EXAMPLE)
    records[0]["checksum"] = "0" * 64
    save_ledger(target, records, seal(records, Ed25519PrivateKey.generate()))
    return target


def _example_key_hex() -> str:
    _, signed_root = load_ledger(EXAMPLE)
    return signed_root.public_key


# --- the published key ---------------------------------------------------------------


def test_the_example_publishes_the_key_that_signed_it() -> None:
    assert EXAMPLE_KEY.is_file()
    assert load_pinned_public_key(EXAMPLE_KEY) == _example_key_hex()


def test_the_example_readme_states_the_same_fingerprint() -> None:
    """The fingerprint travels in a second place, so the pin is not only as good as the folder."""
    readme = (EXAMPLE / "README.md").read_text(encoding="utf-8")
    assert public_key_fingerprint(_example_key_hex()) in readme


def test_fingerprint_is_sha256_of_the_raw_key() -> None:
    key_hex = _example_key_hex()
    assert public_key_fingerprint(key_hex) == hashlib.sha256(bytes.fromhex(key_hex)).hexdigest()


def test_a_pin_file_may_be_pem_or_hex(tmp_path: Path) -> None:
    hex_file = tmp_path / "key.hex"
    hex_file.write_text(_example_key_hex() + "\n", encoding="utf-8")
    assert load_pinned_public_key(hex_file) == load_pinned_public_key(EXAMPLE_KEY)


def test_a_pin_that_is_not_an_ed25519_key_is_rejected(tmp_path: Path) -> None:
    bad = tmp_path / "bad.pem"
    bad.write_text("not a key", encoding="utf-8")
    with pytest.raises(ValueError):
        load_pinned_public_key(bad)


# --- the library verdict -------------------------------------------------------------


def test_forged_ledger_passes_without_a_pin_but_names_its_signer(tmp_path: Path) -> None:
    """Unpinned, a re-sealed ledger is internally consistent - and says whose key that is."""
    records, signed_root = load_ledger(_forge(tmp_path))
    result = verify_ledger(records, signed_root)

    assert result.integrity_ok and result.signature_ok
    assert result.signer_pinned is False
    assert result.signer_fingerprint == public_key_fingerprint(signed_root.public_key)
    assert "signer not pinned" in result.headline


def test_forged_ledger_with_the_original_key_pinned_is_untrusted(tmp_path: Path) -> None:
    records, signed_root = load_ledger(_forge(tmp_path))
    result = verify_ledger(records, signed_root, expected_public_key=_example_key_hex())

    assert result.signer_pinned is True
    assert result.signer_matches_pin is False
    assert result.verified is False
    assert result.headline.startswith("ledger UNTRUSTED SIGNER")


def test_original_ledger_with_its_key_pinned_verifies() -> None:
    records, signed_root = load_ledger(EXAMPLE)
    result = verify_ledger(records, signed_root, expected_public_key=_example_key_hex())

    assert result.verified is True
    assert result.signer_matches_pin is True
    assert result.headline.startswith("ledger VERIFIED")
    assert "signer pinned" in result.headline


# --- the command line: both entry points, one contract -------------------------------


@pytest.mark.parametrize(
    "run",
    [
        lambda argv: cli_main(["ledger", "verify", *argv]),
        module_main,
    ],
    ids=["attestor ledger verify", "python -m attestor.ledger"],
)
class TestExitCodes:
    def test_forged_with_original_pinned_is_exit_3(
        self, run, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([str(_forge(tmp_path)), "--public-key", str(EXAMPLE_KEY)]) == (
            EXIT_UNTRUSTED_SIGNER
        )
        assert "UNTRUSTED SIGNER" in capsys.readouterr().out

    def test_original_pinned_is_exit_0(self, run, capsys: pytest.CaptureFixture[str]) -> None:
        assert run([str(EXAMPLE), "--public-key", str(EXAMPLE_KEY)]) == EXIT_OK
        out = capsys.readouterr().out
        assert out.startswith("ledger VERIFIED")
        assert f"signer_sha256 = {public_key_fingerprint(_example_key_hex())}" in out

    def test_edited_byte_pinned_is_still_tampered_exit_1(
        self, run, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        target = _copy_example(tmp_path)
        records = json.loads((target / "records.json").read_bytes())
        records[0]["system"] = "sys-9"
        (target / "records.json").write_bytes(canonical_json(records))

        assert run([str(target), "--public-key", str(EXAMPLE_KEY)]) == EXIT_TAMPERED
        assert "TAMPERED" in capsys.readouterr().out

    def test_fingerprint_is_printed_even_without_a_pin(
        self, run, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([str(EXAMPLE)]) == EXIT_OK
        assert "signer_sha256 = " in capsys.readouterr().out

    def test_unreadable_pin_is_a_usage_error(
        self, run, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([str(EXAMPLE), "--public-key", str(tmp_path / "absent.pem")]) == EXIT_USAGE
        assert "could not load public key" in capsys.readouterr().err


def test_the_example_public_key_is_a_standard_pem() -> None:
    """Any Ed25519 tool can read the pin, not only this one."""
    key = serialization.load_pem_public_key(EXAMPLE_KEY.read_bytes())
    raw = key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    assert raw.hex() == _example_key_hex()


# --- the HTTP layer offers the same pin, and the demo uses it ------------------------


def test_api_verify_reports_a_foreign_signer(tmp_path: Path) -> None:
    from fastapi.testclient import TestClient

    from attestor.api.main import app

    records, signed_root = load_ledger(_forge(tmp_path))
    body = {
        "records": records,
        "signed_root": signed_root.model_dump(mode="json", exclude_none=True),
        "expected_public_key": _example_key_hex(),
    }
    report = TestClient(app).post("/api/ledger/verify", json=body).json()

    assert report["verified"] is False
    assert report["untrusted_signer"] is True
    assert report["tampered"] is False


def test_the_demo_pins_the_key_it_sealed_with() -> None:
    from fastapi.testclient import TestClient

    from attestor.api.main import app

    verification = TestClient(app).post("/api/demo/run").json()["ledger"]["verification"]
    assert verification["signer_pinned"] is True
    assert verification["verified"] is True
