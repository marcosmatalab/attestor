# Build roadmap

| Phase  | Deliverable | Status |
|--------|-------------|--------|
| **F0** | Scaffold: repo, package, FastAPI `/health`, CI (ruff + pytest) | ✅ |
| **F1** | Deterministic rule engine + bundle `v2026-08` (**legal-text dates**) + golden tests asserting **risk *and* effective dates**. Self-consistent on its own. | ✅ |
| **F2** | **Additive:** scenario bundles + timeline resolution presenting **both** dates (as enacted vs as amended), with the status caveat read from the bundle `meta`. *No rewrite of F1 goldens — not when the Omnibus was a proposal, and not when it became law.* | ✅ |
| **F3** | Annex IV generator + **validated citations** (a citation that doesn't resolve is rejected) + PDF export | ✅ |
| **F4** | C2PA signer: X.509 manifest + optional RFC3161 timestamp. Keys are config-driven and sign inside a `Signer.from_callback` seam, the same interface a KMS/HSM signer plugs into. No KMS backend is implemented. | ✅ |
| **F5** | C2PA verifier — reports signer + assertions + the provenance **nuance** | ✅ |
| **F6** | Ledger Ed25519 + Merkle + RFC3161, **offline** verification via CLI | ✅ |
| **F7** | Governance: ISO/IEC 42001 mapping + FRIA (Art. 27) + Art. 12 logs | ✅ |
| **F8** | Dashboard (Next.js) + polish + demo | ✅ |

> **Bundle schema note (F1 design constraint):** effective dates are stored
> **per obligation**, not as a single global date — so F2 can add the Omnibus
> scenario *additively* without migrating the format or rewriting golden vectors.

---

Each phase has its own page; the index is in the
[repository README](../README.md#deeper-docs).
