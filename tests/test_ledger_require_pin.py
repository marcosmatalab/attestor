"""No ``0`` without a pinned signer.

Until 0.2.0, ``attestor ledger verify`` without ``--public-key`` exited 0 whenever the
records and the signature held together - including for a ledger someone had edited and
re-sealed with their own key. The fingerprint was printed, but a script reading only the
exit code could not tell. Now an unpinned run is its own verdict, ``SIGNER NOT PINNED``
(exit 4). ``--allow-unpinned`` restores the old behaviour for whoever asks for it by name.

The matrix, for both entry points:

    no key                       -> 4    SIGNER NOT PINNED
    no key + --allow-unpinned    -> 0    VERIFIED (signer not pinned)
    the right key                -> 0    VERIFIED (signer pinned)
    another key                  -> 3    UNTRUSTED SIGNER
    one byte edited, any of above-> 1    TAMPERED  (outranks everything)
"""

import json
import shutil
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.canonical import canonical_json
from attestor.cli import main as cli_main
from attestor.ledger import load_ledger, save_ledger, seal, verify_ledger
from attestor.ledger.__main__ import main as module_main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "ledger"
EXAMPLE_KEY = str(EXAMPLE / "public_key.pem")
OK, TAMPERED, UNTRUSTED_SIGNER, NOT_PINNED = 0, 1, 3, 4


def _other_key_file(tmp_path: Path) -> str:
    from attestor.ledger.keys import public_key_hex

    path = tmp_path / "other.hex"
    path.write_text(public_key_hex(Ed25519PrivateKey.generate().public_key()), encoding="utf-8")
    return str(path)


def _edited(tmp_path: Path) -> str:
    target = tmp_path / "edited"
    target.mkdir()
    for name in ("records.json", "signed_root.json"):
        shutil.copy(EXAMPLE / name, target / name)
    records = json.loads((target / "records.json").read_bytes())
    records[0]["system"] = "sys-9"
    (target / "records.json").write_bytes(canonical_json(records))
    return str(target)


RUNNERS = pytest.mark.parametrize(
    "run",
    [lambda argv: cli_main(["ledger", "verify", *argv]), module_main],
    ids=["attestor ledger verify", "python -m attestor.ledger"],
)


@RUNNERS
class TestExitCodeMatrix:
    def test_no_key_is_exit_4(self, run, capsys: pytest.CaptureFixture[str]) -> None:
        assert run([str(EXAMPLE)]) == NOT_PINNED
        out = capsys.readouterr().out
        assert out.startswith("ledger SIGNER NOT PINNED")
        assert "signer_sha256 = 21ffc076" in out

    def test_no_key_with_allow_unpinned_is_exit_0(
        self, run, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([str(EXAMPLE), "--allow-unpinned"]) == OK
        out = capsys.readouterr().out
        assert out.startswith("ledger VERIFIED")
        assert "signer not pinned" in out
        assert "signer_sha256 = 21ffc076" in out

    def test_the_right_key_is_exit_0(self, run) -> None:
        assert run([str(EXAMPLE), "--public-key", EXAMPLE_KEY]) == OK

    def test_another_key_is_exit_3(self, run, tmp_path: Path) -> None:
        assert run([str(EXAMPLE), "--public-key", _other_key_file(tmp_path)]) == UNTRUSTED_SIGNER

    @pytest.mark.parametrize(
        "extra",
        [[], ["--allow-unpinned"], ["--public-key", EXAMPLE_KEY]],
        ids=["no key", "allow-unpinned", "right key"],
    )
    def test_an_edited_byte_is_exit_1_whatever_the_pin(
        self, run, extra: list[str], tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        assert run([_edited(tmp_path), *extra]) == TAMPERED
        assert capsys.readouterr().out.startswith("ledger TAMPERED")

    def test_an_edited_byte_with_another_key_is_still_exit_1(self, run, tmp_path: Path) -> None:
        assert run([_edited(tmp_path), "--public-key", _other_key_file(tmp_path)]) == TAMPERED


def test_pin_and_allow_unpinned_together_is_a_usage_error() -> None:
    """Asking for a pin and for no pin at once is a mistake, not a preference."""
    assert (
        cli_main(
            ["ledger", "verify", str(EXAMPLE), "--public-key", EXAMPLE_KEY, "--allow-unpinned"]
        )
        == 2
    )


# --- the library: same default, same precedence --------------------------------------


def test_library_default_is_not_pinned() -> None:
    records, signed_root = load_ledger(EXAMPLE)
    result = verify_ledger(records, signed_root)
    assert result.verified is False
    assert result.signer_not_pinned is True
    assert result.tampered is False


def test_library_allow_unpinned_restores_verified() -> None:
    records, signed_root = load_ledger(EXAMPLE)
    result = verify_ledger(records, signed_root, allow_unpinned=True)
    assert result.verified is True
    assert result.signer_not_pinned is False


def test_tampered_outranks_not_pinned(tmp_path: Path) -> None:
    records, signed_root = load_ledger(_edited(tmp_path))
    result = verify_ledger(records, signed_root)
    assert result.tampered is True
    assert result.signer_not_pinned is False
    assert result.headline.startswith("ledger TAMPERED")


def test_a_reseal_without_a_pin_no_longer_reads_as_verified(tmp_path: Path) -> None:
    """The case that motivated the change: an attacker's re-seal, verified without a key."""
    records, _ = load_ledger(EXAMPLE)
    records[0]["checksum"] = "0" * 64
    save_ledger(tmp_path, records, seal(records, Ed25519PrivateKey.generate()))
    assert module_main([str(tmp_path)]) == NOT_PINNED


# --- the HTTP layer and the demo -----------------------------------------------------


def _client():
    from fastapi.testclient import TestClient

    from attestor.api.main import app

    return TestClient(app)


def _body(**extra: object) -> dict:
    records, signed_root = load_ledger(EXAMPLE)
    return {
        "records": records,
        "signed_root": signed_root.model_dump(mode="json", exclude_none=True),
        **extra,
    }


def test_api_without_a_key_reports_not_pinned() -> None:
    report = _client().post("/api/ledger/verify", json=_body()).json()
    assert report["verified"] is False
    assert report["signer_not_pinned"] is True
    assert report["headline"].startswith("ledger SIGNER NOT PINNED")


def test_api_allow_unpinned_restores_verified() -> None:
    report = _client().post("/api/ledger/verify", json=_body(allow_unpinned=True)).json()
    assert report["verified"] is True
    assert report["signer_not_pinned"] is False


def test_api_with_the_right_key_verifies() -> None:
    records, signed_root = load_ledger(EXAMPLE)
    body = _body(expected_public_key=signed_root.public_key)
    assert _client().post("/api/ledger/verify", json=body).json()["verified"] is True


def test_the_demo_pins_its_key_so_it_still_verifies() -> None:
    verification = _client().post("/api/demo/run").json()["ledger"]["verification"]
    assert verification["signer_pinned"] is True
    assert verification["signer_not_pinned"] is False
    assert verification["verified"] is True
