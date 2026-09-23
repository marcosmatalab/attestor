# Changelog

Two kinds of entry live here, and they are deliberately kept apart. Software releases
follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). **Regulatory** entries record
changes to the law itself, which have their own dates and are not ours to choose — a
release note that silently mixed the two would make it impossible to tell whether a date
moved because the legislator moved it or because we did.

Full regulatory detail, bundle by bundle, is in
[`docs/regulatory-changelog.md`](docs/regulatory-changelog.md).

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

- The default bundle moved from `omnibus-2026` to `reg-2026-1744`.
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

Absorbing it cost one new bundle file and one changed default: no engine change, no
migration, and not one golden vector rewritten. Effective dates live on each obligation
rather than as a single global date, which is what made an amendment that moved some
dates and not others additive by construction. The two earlier bundles are frozen and
still hash to their June 2026 values.
