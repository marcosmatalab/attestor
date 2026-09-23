# docs/

The depth that does not belong in the root README. Each page assumes you have run the
commands in the README and want to know why something was built the way it was.

| Page | What it covers |
|---|---|
| [`classifier.md`](classifier.md) | The rule engine, the bundle schema, the deliberate simplifications |
| [`timeline.md`](timeline.md) | Comparing two regulatory scenarios in one answer |
| [`regulatory-changelog.md`](regulatory-changelog.md) | How the law changed, and what it cost this repository to absorb |
| [`annex-iv.md`](annex-iv.md) | The dossier, and what a validated citation does and does not mean |
| [`provenance.md`](provenance.md) | C2PA signing and verification, and the integrity/trust split |
| [`ledger.md`](ledger.md) | Merkle, Ed25519, RFC 3161, and what each one actually proves |
| [`governance.md`](governance.md) | ISO/IEC 42001 crosswalk, FRIA scaffold, Art. 12 logs |
| [`api.md`](api.md) | The endpoints, and why the HTTP layer holds no compliance logic |
| [`roadmap.md`](roadmap.md) | What each build phase delivered |

## `dashboard.png`

A genuine screenshot of the running application on its `/demo` page: no mockup, no
synthetic browser chrome, no retouching. Every value in it is engine output — the
classification checksum, the C2PA report with the dev signer reported **untrusted**, and
the ledger **verified** offline.

It is produced by `scripts/capture_dashboard.py`, which exists because this image spent
months lying. The default bundle moved to `reg-2026-1744`, the engine began producing a
different checksum, and the picture kept showing the old one under a caption promising it
was reproducible. A screenshot is a claim, and this was the only claim here that nothing
checked.

So the harness fixes the conditions of the photograph — ports that cannot collide with a
running dev server, a 1200 px viewport at device scale 2, reduced motion, fonts loaded,
the network idle, a production build rather than `next dev` so no development badge is in
frame — and then checks the content before writing anything. The checksum it reads out of
the DOM must equal the one `classify()` produces under the default bundle. If they differ
it writes nothing and exits 1.

What it will not do is retouch. The harness controls the conditions, not the content; if
the page looks wrong the fix belongs in the CSS, which is how the risk badges came to be
measured against WCAG AA rather than left at 4.4:1.

To re-capture:

```bash
make capture          # installs the capture extra, downloads chromium, shoots the page
pytest tests/test_dashboard_capture.py
```

Playwright lives in its own `capture` extra, never in `dev`: CI must not download a
browser for a gate it does not run. The two guard tests need no browser at all.

### `dashboard.meta.json`

The sidecar: when it was captured, from which commit, which profile, the viewport and
device scale, and the PNG's byte size and SHA-256. The capture also writes the verified
checksum into the PNG itself, as a `tEXt` chunk, so the claim travels with the pixels —
`tests/test_dashboard_capture.py` reads it from there rather than from this file, and
then binds this file to the image's bytes. Editing the JSON to make a stale screenshot
look current fails in one direction, and editing the chunk fails in the other.
Re-capturing is the only route.

`dashboard-full.png` is the same page captured end to end at the same settings, kept for
reference; the README shows the cropped one.
