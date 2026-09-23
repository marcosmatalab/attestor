"""``attestor demo`` is the first command a visitor runs; it must run clean.

It used to reach the pipeline through FastAPI's test client, so its output opened with
a deprecation warning from a test-only dependency. Warnings are promoted to errors here,
in a fresh interpreter, so any warning on that path - ours or a dependency's - fails.
"""

import subprocess
import sys

import pytest

from attestor.cli import main


def test_demo_runs_with_deprecation_warnings_as_errors() -> None:
    completed = subprocess.run(
        [sys.executable, "-W", "error::DeprecationWarning", "-m", "attestor.cli", "demo"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    assert "Warning" not in completed.stderr
    assert "ledger VERIFIED" in completed.stdout


def test_demo_does_not_load_the_web_framework() -> None:
    """The cause, not the symptom: the demo path imports neither FastAPI nor Starlette."""
    probe = (
        "import sys\n"
        "from attestor.cli import main\n"
        "main(['demo', '--json'])\n"
        "loaded = sorted(m for m in sys.modules if m.split('.')[0] in {'fastapi', 'starlette'})\n"
        "sys.stderr.write(repr(loaded))\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, timeout=120, check=False
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stderr.strip() == "[]"


def test_the_api_demo_and_the_cli_demo_are_one_pipeline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    from fastapi.testclient import TestClient

    from attestor.api.main import app

    api = TestClient(app).post("/api/demo/run").json()
    assert main(["demo", "--json"]) == 0
    import json

    cli = json.loads(capsys.readouterr().out)
    assert cli["classification"]["checksum"] == api["classification"]["checksum"]
    assert cli["ledger"]["records"][:2] == api["ledger"]["records"][:2]
