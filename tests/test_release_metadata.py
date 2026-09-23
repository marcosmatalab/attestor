"""The install instructions point at the release that is actually tagged.

Attestor is installed from a tagged release on GitHub, never from a package index: no
text may promise a ``pip install attestor`` that does not exist. The quickstart clones
the tag of the current version, so bumping ``__version__`` without updating the READMEs
and the CHANGELOG fails here.
"""

import re
from pathlib import Path

import pytest

from attestor import __version__

ROOT = Path(__file__).resolve().parents[1]
READMES = ["README.md", "README.es.md"]
TEXT_FILES = [
    *READMES,
    "CHANGELOG.md",
    "examples/ledger/README.md",
    *map(str, Path(ROOT / "docs").glob("*.md")),
]


@pytest.mark.parametrize("name", READMES)
def test_the_quickstart_clones_the_current_tag(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    assert (
        f"git clone --branch v{__version__} https://github.com/marcosmatalab/attestor.git" in text
    )


def test_the_changelog_has_a_section_for_the_current_version() -> None:
    assert f"## [{__version__}]" in (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", TEXT_FILES)
def test_nothing_promises_a_package_index(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    assert not re.search(r"pypi|pip install attestor\b", text, re.IGNORECASE), name
