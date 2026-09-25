"""What the docs say about how the Omnibus was absorbed must match ``git log``.

Two claims used to contradict the history. The docs dated the in-force bundle to the
law's entry into force (27 July 2026), while ``git log`` adds it on 22 September; and
they said absorbing it changed no engine code and no golden, while that same commit
edited ``classifier/timeline.py``, ``classifier/bundle.py`` and ``annexiv/*`` and
renamed a field in ``tests/golden/annexiv-v2026-08.yaml``.

The facts are pinned below and checked against the repository's history, so the prose
cannot drift from them again. The history check needs the full clone; CI fetches it,
and refuses to skip it.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# --- the facts, as git records them ---------------------------------------------------
BUNDLE_COMMIT = "00a566d"
BUNDLE_ADDED = "2026-09-22"  # the day reg-2026-1744 was added and made the default
LAW_IN_FORCE = "2026-07-27"  # the day the Regulation itself became binding
BUNDLE_FILE = "src/attestor/classifier/rules/reg-2026-1744.yaml"
ENGINE_FILES_CHANGED = {
    "src/attestor/classifier/timeline.py",
    "src/attestor/classifier/bundle.py",
    "src/attestor/annexiv/model.py",
    "src/attestor/annexiv/generator.py",
    "src/attestor/annexiv/pdf.py",
    "tests/golden/annexiv-v2026-08.yaml",
}
UNTOUCHED = {
    "src/attestor/classifier/rules/v2026-08.yaml",
    "src/attestor/classifier/rules/omnibus-2026.yaml",
    "tests/golden/v2026-08.yaml",
    "tests/golden/omnibus-2026.yaml",
}

DOCS = [
    "README.md",
    "README.es.md",
    "CHANGELOG.md",
    "docs/regulatory-changelog.md",
    "docs/timeline.md",
    "docs/roadmap.md",
]

# Sentences the history refutes. Each must never come back.
REFUTED = [
    r"no engine (logic )?change",
    r"no engine logic changed",
    r"one (new )?bundle file and one changed default",
    r"adding one bundle file and changing one default",
    r"ningún cambio en el motor",
    r"un fichero de bundle nuevo y un valor por defecto cambiado",
    r"single new file",
    r"un único fichero nuevo",
    r"moved from `omnibus-2026`",
    r"no rewritten (golden vector|reference test case)",
    r"ningún caso de prueba de referencia reescrito",
]


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _history_available() -> bool:
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        return False
    try:
        _git("cat-file", "-e", f"{BUNDLE_COMMIT}^{{commit}}")
    except subprocess.CalledProcessError:
        return False
    return True


@pytest.fixture(scope="module")
def history() -> None:
    if not _history_available():
        if os.environ.get("CI"):
            pytest.fail("CI must check out full history (fetch-depth: 0) for this test")
        pytest.skip("git history not available")


@pytest.mark.usefixtures("history")
def test_git_dates_the_bundle_as_the_docs_do() -> None:
    added = _git("log", "--diff-filter=A", "--format=%h %ad", "--date=short", "--", BUNDLE_FILE)
    assert added == f"{BUNDLE_COMMIT} {BUNDLE_ADDED}"


@pytest.mark.usefixtures("history")
def test_git_shows_the_engine_changes_the_docs_admit() -> None:
    changed = set(_git("show", "--name-only", "--format=", BUNDLE_COMMIT).splitlines())
    assert changed >= ENGINE_FILES_CHANGED
    assert not (UNTOUCHED & changed)


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


@pytest.mark.parametrize("name", DOCS)
def test_no_doc_repeats_a_refuted_claim(name: str) -> None:
    text = _text(name)
    found = [p for p in REFUTED if re.search(p, text, re.IGNORECASE)]
    assert not found, f"{name} still says: {found}"


@pytest.mark.parametrize(
    "name", ["README.md", "README.es.md", "CHANGELOG.md", "docs/regulatory-changelog.md"]
)
def test_the_docs_date_the_bundle_from_git(name: str) -> None:
    text = _text(name)
    assert BUNDLE_ADDED in text
    assert BUNDLE_COMMIT in text


def test_the_changelog_row_for_entry_into_force_does_not_date_the_bundle() -> None:
    """The law's date and the repository's date are different facts, on different rows."""
    for line in _text("docs/regulatory-changelog.md").splitlines():
        if LAW_IN_FORCE in line and line.startswith("|"):
            assert "default" not in line and "added" not in line, line
