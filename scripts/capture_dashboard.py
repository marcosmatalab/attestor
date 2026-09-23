"""Re-capture `docs/dashboard.png` under controlled, reproducible conditions.

A screenshot in a README is a claim, and it is the only claim in this repository that
no test could previously check. The June 2026 capture went stale exactly that way: the
default bundle changed, the engine started producing a different checksum, and the image
kept showing the old one for months while the caption underneath said it was reproducible.

So this harness does two things. It fixes the *conditions* of the photograph - ports that
cannot collide with a running dev server, a fixed viewport, a fixed device scale, reduced
motion, fonts fully loaded, the network idle - and then it *checks the content* before
writing anything: the checksum read out of the DOM must equal the checksum `classify()`
produces under the default bundle. If they differ, nothing is written and the exit code
is 1. A capture that cannot prove what it shows is worse than no capture.

What it deliberately does NOT do: any retouching. No synthetic browser chrome, no drop
shadows implying a different application, no moving elements to photograph better. The
harness controls the conditions, not the content - `docs/README.md` claims this is a
genuine screenshot of the running app, and that sentence is worth more than any polish.
If the page looks wrong, the fix belongs in the CSS.

    pip install -e ".[capture]"
    python -m playwright install chromium
    python scripts/capture_dashboard.py

Playwright lives in its own extra, never in `dev`: CI must not pay to download a browser
for a gate it does not run.
"""

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import socket
import struct
import subprocess
import sys
import time
import zlib
from datetime import UTC, datetime
from typing import Any

from playwright.sync_api import Browser, Page, sync_playwright

from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle

ROOT = pathlib.Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
DOCS = ROOT / "docs"
SCRATCH = ROOT / ".capture"

# Deliberately not 8000/3000: a developer with the app already running should be able to
# re-capture without killing it, and a half-shut-down server on the usual port is a
# silent way to photograph the wrong build.
API_PORT = 8010
WEB_PORT = 3010

VIEWPORT_WIDTH = 1200
DEVICE_SCALE = 2

# The profile the API's /demo/run endpoint uses. Kept here explicitly so the meta file
# records what was photographed rather than leaving the reader to guess.
PROFILE = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
PROFILE_LABEL = "provider / annex III: employment"

DIGEST = re.compile(r"\b[0-9a-f]{64}\b")

# Read the classification checksum out of the rendered page rather than out of the API
# response: the point is to prove the *pixels* show it, not that the backend computed it.
CHECKSUM_FROM_DOM = """
() => {
  for (const dt of document.querySelectorAll('dt')) {
    if (dt.textContent.trim() === 'Checksum') {
      const dd = dt.parentElement && dt.parentElement.querySelector('dd');
      if (dd) return dd.textContent.trim();
    }
  }
  return null;
}
"""

# The content column is centred inside the viewport, so the gutter it already leaves is
# the page's own margin. Reusing it, rather than inventing a number, is what makes the
# left, right and bottom margins identical.
GEOMETRY = """
() => {
  const container = document.querySelector('main .container');
  const rect = container.getBoundingClientRect();
  return {
    left: rect.left + window.scrollX,
    width: rect.width,
    bottom: rect.bottom + window.scrollY,
    documentWidth: document.documentElement.clientWidth,
  };
}
"""


def log(message: str) -> None:
    print(f"[capture] {message}", flush=True)


def expected_checksum() -> str:
    """What the engine produces today, under the default bundle."""
    return classify(PROFILE, load_bundle()).checksum


def port_is_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        return probe.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, what: str, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if port_is_open(port):
            log(f"{what} is up on {port}")
            return
        time.sleep(0.5)
    raise RuntimeError(f"{what} never came up on port {port} within {timeout:.0f}s")


def refuse_if_busy() -> None:
    for port, what in ((API_PORT, "backend"), (WEB_PORT, "frontend")):
        if port_is_open(port):
            raise RuntimeError(
                f"port {port} is already serving something; {what} would photograph it. "
                "Stop it and re-run."
            )


def spawn(command: list[str], cwd: pathlib.Path, env: dict[str, str], name: str) -> Any:
    """Run a server, sending its noise to `.capture/` so a failure can be read afterwards."""
    SCRATCH.mkdir(exist_ok=True)
    handle = (SCRATCH / f"{name}.log").open("w", encoding="utf-8")
    return subprocess.Popen(  # noqa: S603
        command, cwd=cwd, env=env, stdout=handle, stderr=subprocess.STDOUT, text=True
    )


def stop(process: Any) -> None:
    """Kill the whole process tree.

    `npm run start` is a shim that spawns `next` as a child, and on Windows terminating
    the shim leaves the server holding the port. The first run of this harness did
    exactly that, and the second refused to start because port 3010 was still busy - a
    better failure than photographing a stale build, but still a bug.
    """
    if process.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(  # noqa: S603
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
    else:
        process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()


def npm() -> str:
    found = shutil.which("npm") or shutil.which("npm.cmd")
    if not found:
        raise RuntimeError("npm is not on PATH, so the frontend cannot be built")
    return found


def build_frontend(env: dict[str, str]) -> None:
    """A production build, not `next dev`.

    `next dev` paints a development indicator over the corner of the page. Photographing
    it would mean either shipping that badge in the README or cropping it out, and
    cropping to hide something is the first step onto the wrong road.
    """
    log("building the frontend (NEXT_PUBLIC_API_BASE_URL is inlined at build time)")
    result = subprocess.run(  # noqa: S603
        [npm(), "run", "build"], cwd=WEB, env=env, capture_output=True, text=True
    )
    if result.returncode != 0:
        (SCRATCH / "build.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        raise RuntimeError("the frontend build failed; see .capture/build.log")


def render(browser: Browser, expected: str) -> tuple[Page, dict[str, float]]:
    context = browser.new_context(
        viewport={"width": VIEWPORT_WIDTH, "height": 1000},
        device_scale_factor=DEVICE_SCALE,
        locale="en-US",
        color_scheme="light",
        reduced_motion="reduce",
    )
    page = context.new_page()
    page.goto(f"http://127.0.0.1:{WEB_PORT}/demo", wait_until="networkidle")

    page.get_by_role("button", name="Run the demo").click()

    # Wait for real content, not for a timer. Each of these is a thing the engine had to
    # produce: a digest, the ledger verdict, and the trust verdict that must never be
    # quietly upgraded to "trusted" by a UI change.
    page.wait_for_function(
        "() => /\\b[0-9a-f]{64}\\b/.test(document.body.innerText)", timeout=60_000
    )
    page.get_by_text("VERIFIED", exact=False).first.wait_for(timeout=30_000)
    page.get_by_text("UNTRUSTED", exact=False).first.wait_for(timeout=30_000)
    page.wait_for_load_state("networkidle")
    page.evaluate("() => document.fonts.ready")

    shown = page.evaluate(CHECKSUM_FROM_DOM)
    if shown != expected:
        raise RuntimeError(
            "ABORTED, nothing written. The page shows a checksum the engine does not "
            f"produce.\n  in the DOM: {shown}\n  from classify(): {expected}"
        )
    log(f"the DOM shows the engine's checksum: {expected}")

    geometry = page.evaluate(GEOMETRY)
    return page, geometry


def shoot(page: Page, geometry: dict[str, float]) -> int:
    """Write both images. Returns the margin actually used, in CSS pixels."""
    gutter = round(geometry["left"])
    if gutter <= 0:
        raise RuntimeError(f"the content column is not centred (left={geometry['left']})")

    height = round(geometry["bottom"]) + gutter
    page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": height})
    page.wait_for_timeout(250)

    DOCS.mkdir(exist_ok=True)
    page.screenshot(
        path=str(DOCS / "dashboard.png"),
        clip={"x": 0.0, "y": 0.0, "width": float(VIEWPORT_WIDTH), "height": float(height)},
    )
    page.screenshot(path=str(DOCS / "dashboard-full.png"), full_page=True)
    return gutter


def png_size(data: bytes) -> tuple[int, int]:
    width, height = struct.unpack(">II", data[16:24])
    return int(width), int(height)


def stamp_checksum(path: pathlib.Path, checksum: str) -> None:
    """Write the verified checksum into the PNG itself, as a tEXt chunk.

    Without this, the pair of guard tests has a hole big enough to walk through: if the
    engine's checksum moves, editing one string in `dashboard.meta.json` makes both of
    them green again while the image still shows the old value. Recording the checksum
    in the file whose bytes are hashed removes that shortcut - the claim now travels
    with the pixels, and changing it changes the hash the meta has to match.

    It is metadata, not retouching. Not one pixel differs.
    """
    data = path.read_bytes()
    end = data.rindex(b"IEND") - 4  # start of the IEND length field
    payload = b"attestor-checksum\x00" + checksum.encode("ascii")
    chunk = (
        struct.pack(">I", len(payload))
        + b"tEXt"
        + payload
        + struct.pack(">I", zlib.crc32(b"tEXt" + payload) & 0xFFFFFFFF)
    )
    path.write_bytes(data[:end] + chunk + data[end:])


def commit() -> str:
    result = subprocess.run(  # noqa: S603
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() or "unknown"


def write_meta(checksum: str, margin: int) -> dict[str, Any]:
    stamp_checksum(DOCS / "dashboard.png", checksum)
    data = (DOCS / "dashboard.png").read_bytes()
    width, height = png_size(data)
    meta = {
        "captured_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": commit(),
        "classification_checksum": checksum,
        "profile": PROFILE_LABEL,
        "viewport": {"width": VIEWPORT_WIDTH, "height": height // DEVICE_SCALE},
        "device_scale_factor": DEVICE_SCALE,
        "margin_css_px": margin,
        "png_sha256": hashlib.sha256(data).hexdigest(),
        "png_bytes": len(data),
        "png_pixels": {"width": width, "height": height},
    }
    (DOCS / "dashboard.meta.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return meta


def capture() -> int:
    expected = expected_checksum()
    log(f"the engine's checksum for {PROFILE_LABEL} is {expected}")
    refuse_if_busy()

    env = {
        **os.environ,
        "NEXT_PUBLIC_API_BASE_URL": f"http://127.0.0.1:{API_PORT}",
        # The backend's allow-list is config-driven, so the capture port is added here
        # rather than by disabling the browser's same-origin checks. Photographing a
        # page under weakened browser security would hide exactly the kind of failure
        # this harness exists to catch.
        "CORS_ORIGINS": f"http://localhost:{WEB_PORT},http://127.0.0.1:{WEB_PORT}",
    }
    build_frontend(env)

    backend = spawn(
        [sys.executable, "-m", "uvicorn", "attestor.api.main:app", "--port", str(API_PORT)],
        ROOT,
        env,
        "backend",
    )
    frontend = spawn([npm(), "run", "start", "--", "--port", str(WEB_PORT)], WEB, env, "frontend")
    try:
        wait_for_port(API_PORT, "backend", timeout=60)
        wait_for_port(WEB_PORT, "frontend", timeout=90)

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page, geometry = render(browser, expected)
                margin = shoot(page, geometry)
            finally:
                browser.close()
    finally:
        for process in (frontend, backend):
            stop(process)

    meta = write_meta(expected, margin)
    log(f"wrote docs/dashboard.png  {meta['png_pixels']['width']}x{meta['png_pixels']['height']}px")
    log(f"      sha256 {meta['png_sha256']}")
    log(f"      margin {margin} CSS px on the left, right and bottom")
    log("wrote docs/dashboard.meta.json and docs/dashboard-full.png")
    log("now run: pytest tests/test_dashboard_capture.py")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--print-checksum",
        action="store_true",
        help="print the checksum the engine produces today and exit, capturing nothing",
    )
    args = parser.parse_args(argv)

    if args.print_checksum:
        print(expected_checksum())
        return 0
    try:
        return capture()
    except RuntimeError as failure:
        print(f"[capture] {failure}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
