"""End-to-end CLI tests: offline verification driven only by files on disk.

The CLI exit code is the tamper check (integrity AND signature) only. A valid ledger
timestamped by an unrecognised TSA still exits 0 — TSA trust is reported, not enforced.
"""

import json
import shutil
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.canonical import canonical_json
from attestor.ledger import build_timestamp_info, save_ledger, seal
from attestor.ledger.__main__ import main

_TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
_RECORDS = [
    {"type": "dossier", "id": "sys-1", "sha256": "aa"},
    {"type": "c2pa", "id": "img-1", "sha256": "bb"},
    {"type": "dossier", "id": "sys-2", "sha256": "cc"},
]
_FIXTURES = Path(__file__).parent / "fixtures" / "ledger"


def test_cli_accepts_a_valid_ledger(tmp_path: Path) -> None:
    save_ledger(tmp_path, _RECORDS, seal(_RECORDS, _TEST_KEY))
    assert main([str(tmp_path)]) == 0


def test_cli_detects_tampering(tmp_path: Path) -> None:
    save_ledger(tmp_path, _RECORDS, seal(_RECORDS, _TEST_KEY))
    # Alter a record on disk after sealing -> recomputed root no longer matches.
    records_file = tmp_path / "records.json"
    data = json.loads(records_file.read_bytes())
    data[0]["sha256"] = "ff"
    records_file.write_bytes(canonical_json(data))

    assert main([str(tmp_path)]) == 1


def test_cli_timestamped_untrusted_tsa_is_exit_0(tmp_path: Path) -> None:
    token = (_FIXTURES / "timestamp.tsr").read_bytes()
    signed = seal(_RECORDS, _TEST_KEY).model_copy(update={"timestamp": build_timestamp_info(token)})
    save_ledger(tmp_path, _RECORDS, signed)
    shutil.copytree(_FIXTURES / "tsa", tmp_path / "tsa")

    # Valid ledger + valid token from an unrecognised TSA -> still exit 0.
    assert main([str(tmp_path)]) == 0


def test_cli_usage_error_returns_2() -> None:
    assert main([]) == 2


def test_cli_missing_directory_returns_2(tmp_path: Path) -> None:
    assert main([str(tmp_path / "nope")]) == 2
