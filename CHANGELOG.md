# Changelog

Two kinds of entry live here, and they are deliberately kept apart. Software releases
follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). **Regulatory** entries record
changes to the law itself, which have their own dates and are not ours to choose — a
release note that silently mixed the two would make it impossible to tell whether a date
moved because the legislator moved it or because we did.

Full regulatory detail, bundle by bundle, is in
[`docs/regulatory-changelog.md`](docs/regulatory-changelog.md).

## [0.2.0] — 2026-09-23

A security fix that needed a new feature to land, plus three corrections. **Why 0.2.0:**
`--public-key` and exit code `3` are new, backward-compatible functionality, which
Semantic Versioning puts in a MINOR release; a PATCH may not add features. It is not a
MAJOR change: exit codes `0`, `1` and `2` keep their meaning, and nothing was removed.

### Security

- **The ledger verifier trusted any signer.** It checked the signature with the public key
  stored inside `signed_root.json`, so records edited and re-sealed with a fresh key
  verified as `VERIFIED`, exit 0. `attestor ledger verify DIR --public-key FILE` (and the
  same flag on `python -m attestor.ledger`) now pins the expected key; a ledger sealed by
  any other key is `UNTRUSTED SIGNER`, exit `3`. Tampering still outranks it (exit `1`).
  The signing key's SHA-256 fingerprint is printed on every run. Without a pin, a
  consistent ledger still exits `0` and says `signer not pinned`; the reasoning is in
  [`docs/ledger.md`](docs/ledger.md#pinning-the-signer). (#26)

### Added

- `examples/ledger/public_key.pem`, the key that signed the example ledger, written by
  `scripts/make_example_ledger.py`. Its fingerprint,
  `21ffc076b7eef2cce6884e0c6b382a9ad72e4ba3d4b7a971cc1f601a8bac5544`, is also stated in
  `examples/ledger/README.md` and in these release notes. (#26)
- `expected_public_key` on `POST /api/ledger/verify`, and `tampered` / `untrusted_signer`
  in its response. The demo pins the key it sealed with. (#26)

### Fixed

- `attestor demo` no longer starts with a `StarletteDeprecationWarning`. It reached the
  pipeline through FastAPI's test client; the pipeline now lives in `attestor.demo` and
  both the CLI and `POST /api/demo/run` call it directly. A plain `pip install` is enough
  to run it; the `dev` extra is no longer needed for the demo. (#27)
- The demo's C2PA AI-disclosure label names `example-model` instead of a commercial model
  the project does not use. (#28)
- The docs dated the in-force bundle to 2026-07-27 and said absorbing it changed no engine
  code. `git log` adds it on 2026-09-22 in `66ec7c9`, a commit that also edited
  `classifier/timeline.py`, `classifier/bundle.py` and `annexiv/*`; the docs now say so,
  and a test checks them against the history. (#29)
- `docs/dashboard.png` re-captured: it showed the ledger headline from before the pin. (#30)

### Changed

- Installation is from a tagged release on GitHub; nothing is published to a package index.

## [0.1.0] — 2026-09-23

First tagged release. The engine has been working since June 2026; this is the point at
which every claim made about it is checkable by a command.

### Added

- `attestor` CLI: `classify`, `ledger verify`, `demo`. Exit codes are the interface —
  a tampered ledger is exit 1, not a message a script has to parse.
- `examples/ledger/`: a signed ledger committed to the repository, so a third party can
  verify one offline without generating anything first.
- `reg-2026-1744` bundle, the law in force, and now the default.
- Gates that bite: 27 literal checksum anchors, an AST-walked architecture contract, a
  Makefile-parsing test that every tool the gates run is declared, and a capture test
  that fails when the README's screenshot stops matching the engine.
- `scripts/capture_dashboard.py` and `scripts/run_offline.py`.

### Changed

- The default bundle moved from `v2026-08` to `reg-2026-1744`, in the engine and the API
  (commit `66ec7c9`, 2026-09-22).
- The README dropped from 574 lines to 249, and its depth moved into `docs/`.
- CI runs `make check`, so the workflow and the Makefile cannot drift apart.

### Removed

- The static `tests-228-passing` badge. It was wrong, and nothing would have told us.
- Every claim a `grep` could disprove: the KMS backend, the database, the multi-tenant
  story. The signing seam is real; the integration was never written.

### Fixed

- The `dev` extra declared three packages while the gates ran six. On a clean runner
  `make check` died at `mypy: No such file or directory`; it passed locally only because
  the tools resolved from another virtualenv on `PATH`.

## Regulatory

### 2026-07-27 — Regulation (EU) 2026/1744 (Digital Omnibus on AI) entered into force

Adopted by the Council on 29 June 2026, published in the Official Journal on 24 July
2026, binding since 27 July 2026. It amends Reg. (EU) 2024/1689, moving Annex III
high-risk obligations to 2 December 2027 and Annex I embedded systems to 2 August 2028.

The repository absorbed it on 2026-09-22 (commit `66ec7c9`): the `reg-2026-1744` bundle,
the default moved to it, and three small engine edits in the same commit (the timeline
compares against the bundle in force; the Annex IV field `provisional_note` became
`status_note`, and its golden followed). No rule was migrated, and the two earlier bundles
and their classification golden vectors are unchanged. Effective dates live on each obligation
rather than as a single global date, which is what made an amendment that moved some
dates and not others additive by construction. The two earlier bundles are frozen and
still hash to their June 2026 values.
