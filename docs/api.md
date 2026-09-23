# Dashboard and HTTP API (F8)

A **thin presentation layer** over the engine: a FastAPI surface and a Next.js 16 dashboard.
There is **zero compliance logic** in either — every figure, date, checksum, and verdict comes
from F1–F7, which remain the single source of truth.

- **`/api` endpoints** are thin wrappers: `POST /api/classify`, `/api/timeline` (dual dates),
  `/api/annex-iv` (+ `/pdf`), `/api/governance/crosswalk`, `/api/governance/fria`,
  `/api/provenance/verify`, `/api/ledger/verify`, and `/api/demo/run`. Gated engine errors
  surface as HTTP 422 with the engine's own message; computed properties (`headline`,
  `effective_dates`) are serialized verbatim — never reimplemented in the API.
- **The decisive test:** each endpoint's response is compared to a direct engine call (identical
  checksum, identical report) — the proof that nothing is mocked or hardcoded.
- **The dashboard** (`web/`) renders those outputs verbatim: the risk badge and reproducible
  checksum, the dual legal-text vs Omnibus timeline with the provisional caveat, the Annex IV
  scaffold, the ISO/IEC 42001 crosswalk, the FRIA scaffold, and the C2PA + ledger verification.

### End-to-end demo

`POST /api/demo/run` (the **End-to-end demo** page) runs one example **high-risk provider** path
live: classify → Annex IV → sign an AI output (C2PA) → verify → anchor in the ledger → verify the
ledger offline. Signing and sealing use **ephemeral dev keys** generated per request (never
committed), so the C2PA signer is honestly **untrusted** and the ledger still verifies offline.

The pipeline itself is `attestor.demo.run_demo`, an engine-side function. The endpoint and
`attestor demo` both call it; the CLI does **not** go through HTTP. It used to, via FastAPI's
test client, which put a test-only dependency — and its deprecation warnings — on the first
command a visitor runs. `tests/test_architecture.py` now forbids `fastapi` and `starlette` in
engine modules, and `tests/test_demo_cli.py` runs the demo with `-W error::DeprecationWarning`.

**Decision: FastAPI and Starlette keep lower bounds only** (`fastapi>=0.115`, Starlette via
FastAPI).

- *Why:* the warning was a symptom of the CLI depending on the web stack at all; that
  dependency is gone, so a cap would pin around a problem that no longer exists. An upper
  bound on a framework also blocks its security fixes until someone lifts it by hand.
- *What it costs:* a breaking FastAPI or Starlette release can break `api/` without a
  change here. CI resolves the latest compatible versions on every push and runs the API
  tests against them, so the break shows up as a red build rather than in production; the
  engine and the CLI demo cannot be affected, because they no longer import either.

### UI honesty (no overselling)

- A persistent banner: a portfolio demonstration, not legal advice or a compliance product. The
  words "compliant" / "certified" / "verified" never stand alone.
- **Dual dates always**, with the Omnibus "pending adoption" caveat — never a single date as "the"
  date.
- **"Validated"** is shown to mean a citation *resolves and traces* to an emitted obligation, not
  that it substantiates a claim.
- **C2PA** uses the F5 headline verbatim: "integrity Valid" never appears without the trust
  qualifier, and the dev signer is reported **UNTRUSTED**.
- **The ledger** is described as an append-only log verifiable offline — **not a blockchain**.
