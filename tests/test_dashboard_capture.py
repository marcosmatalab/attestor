"""The screenshot in the README must show what the engine produces today.

`docs/dashboard.png` is a claim, and it was the one claim here that nothing checked. It
went stale for months: the default bundle moved to `reg-2026-1744`, the engine started
producing a different checksum, and the image kept showing the old one under a caption
promising it was reproducible.

Two tests close that gap, and they need each other.

The first reads the checksum out of the PNG itself - `scripts/capture_dashboard.py`
writes it into a tEXt chunk, but only after verifying it against the live DOM - and
compares it with a fresh `classify()` call. The claim therefore travels with the pixels.

The second re-hashes the PNG against `docs/dashboard.meta.json`. That is what stops the
cheap repair: if the engine's checksum moves, editing the meta file cannot make the first
test green, because the first test never reads the meta; and editing the chunk inside the
PNG changes its sha256, which this test catches. Fixing it means re-capturing, which is
the point.

Neither test needs Playwright or a browser. They read two committed files and call the
engine, which is why they run on every CI job while the capture extra stays out of `dev`.
Regenerate both files together with `make capture`.
"""

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import pytest

from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle

DOCS = Path(__file__).resolve().parents[1] / "docs"
SCREENSHOT = DOCS / "dashboard.png"
META = DOCS / "dashboard.meta.json"

STAMP = re.compile(rb"attestor-checksum\x00([0-9a-f]{64})")


@pytest.fixture(scope="module")
def png() -> bytes:
    return SCREENSHOT.read_bytes()


@pytest.fixture(scope="module")
def meta() -> dict[str, Any]:
    return dict(json.loads(META.read_text(encoding="utf-8")))


def test_the_screenshot_shows_the_checksum_the_engine_produces_today(png: bytes) -> None:
    """Read from the image, never from the sidecar: the sidecar is the editable one."""
    stamped = STAMP.search(png)
    assert stamped, "docs/dashboard.png carries no checksum stamp; re-run `make capture`"

    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    live = classify(profile, load_bundle())

    assert stamped.group(1).decode() == live.checksum, (
        "docs/dashboard.png shows a checksum the engine no longer produces. "
        "Re-capture it with `make capture`; editing the meta file will not help."
    )


def test_the_meta_cannot_be_edited_without_re_capturing(png: bytes, meta: dict[str, Any]) -> None:
    """Binds the sidecar to the bytes, so the stamp above cannot be quietly rewritten."""
    assert meta["png_bytes"] == len(png)
    assert meta["png_sha256"] == hashlib.sha256(png).hexdigest()
    assert meta["classification_checksum"] == STAMP.search(png).group(1).decode()  # type: ignore[union-attr]
