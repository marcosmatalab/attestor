# Build roadmap

Every phase shipped, one pull request each.

| Phase | Deliverable | |
|---|---|---|
| **F0** | Scaffold: package, FastAPI `/health`, CI | Y |
| **F1** | Deterministic rule engine, bundle `v2026-08`, golden vectors on risk *and* dates | Y |
| **F2** | Additive scenario bundles and dual-timeline resolution, caveat read from bundle `meta` | Y |
| **F3** | Annex IV generator, fail-closed citation validator, byte-stable PDF | Y |
| **F4** | C2PA signer: X.509 manifest, optional RFC3161, `Signer.from_callback` seam (no KMS backend) | Y |
| **F5** | C2PA verifier reporting integrity and signer trust separately | Y |
| **F6** | Ledger: Ed25519 + RFC 6962 Merkle + RFC3161 codec, offline CLI verification | Y |
| **F7** | Governance: ISO/IEC 42001 map, FRIA (Art. 27), Art. 12 / 26(6) logs | Y |
| **F8** | Next.js dashboard with i18n, and the demo pipeline | Y |

---

Each phase is documented in its own file; see the
[repository README](../README.md) for the index.
