# Attestor

> **Status: `pre-alpha` · 🚧 under construction.** F0 (scaffold) only. No business logic yet.

**Attestor is a deterministic EU AI Act compliance engine.** You register an AI
system and Attestor (1) **classifies its risk** under the EU AI Act (prohibited /
high / limited / minimal) and resolves **which obligations apply and from which
date** — including the *Digital Omnibus* timeline; (2) **generates the Annex IV
technical dossier** with citations **validated** against a versioned regulatory
bundle (no hallucinated references); (3) **signs AI outputs with C2PA Content
Credentials** for verifiable provenance (Art. 50); and (4) **anchors everything in
a cryptographic ledger** (Ed25519 + Merkle + RFC3161) that a third party can
verify **offline**.

The classification decision is a **rule engine, not an LLM** — same input produces
the same output, with a checksum, reproducible for an auditor.

---

## Architecture

```
  Register AI system ──▶ ┌──────────────────────────────────────────────┐
   (questionnaire)       │                  ATTESTOR                     │
                         │                                              │
                         │   ┌──────────────────────────────────────┐   │
                         │   │  DETERMINISTIC CLASSIFIER (rules)     │   │
                         │   │   risk + obligations + EFFECTIVE      │   │
                         │   │   DATES  (versioned bundle, Omnibus-  │   │
                         │   │   aware)   → checksum + golden        │   │
                         │   └──────────────────┬───────────────────┘   │
                         │                      ▼                        │
                         │   ┌──────────────────────────────────────┐   │
                         │   │  ANNEX IV GENERATOR                   │   │
                         │   │   citations validated → articles      │   │
                         │   └──────────────────┬───────────────────┘   │
                         │                      ▼                        │
   AI output ───────────▶│   ┌──────────────────────────────────────┐   │
                         │   │  C2PA SIGNER / VERIFIER               │   │
                         │   │   manifest (X.509) + RFC3161          │   │
                         │   └──────────────────┬───────────────────┘   │
                         │                      ▼                        │
                         │   ┌──────────────────────────────────────┐   │
                         │   │  LEDGER  Ed25519 + Merkle + RFC3161   │   │
                         │   │   anchors dossier + C2PA manifests    │   │
                         │   └──────────────────┬───────────────────┘   │
                         └──────────────────────┼───────────────────────┘
                                                ▼
                          OFFLINE verification by a third party (auditor)
```

---

## Quickstart

```bash
# 1. Install (editable, with dev tooling)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 2. Run the API
uvicorn attestor.api.main:app --reload

# 3. Probe it
curl http://127.0.0.1:8000/health
# {"status":"ok","service":"attestor","version":"0.0.1","environment":"development"}

# 4. Run the checks (everything green before any commit)
ruff check .
ruff format --check .
pytest
```

Configuration is read from environment variables / a local `.env` (see
[`.env.example`](.env.example)).

---

## Roadmap

| Phase  | Deliverable | Status |
|--------|-------------|--------|
| **F0** | Scaffold: repo, package, FastAPI `/health`, CI (ruff + pytest) | ✅ |
| **F1** | Deterministic rule engine + bundle `v2026-08` (**legal-text dates**) + golden tests asserting **risk *and* effective dates**. Self-consistent on its own. | ✅ |
| **F2** | **Additive:** Omnibus-scenario bundle + timeline resolution presenting **both** dates (legal text vs Omnibus provisional) + the "pending formal adoption" caveat. *No rewrite of F1 goldens.* | ⏳ |
| **F3** | Annex IV generator + **validated citations** (a citation that doesn't resolve is rejected) + PDF export | ⏳ |
| **F4** | C2PA signer — manifest (X.509) + RFC3161 timestamp, keys via KMS/HSM | ⏳ |
| **F5** | C2PA verifier — reports signer + assertions + the provenance **nuance** | ⏳ |
| **F6** | Ledger Ed25519 + Merkle + RFC3161, **offline** verification via CLI | ⏳ |
| **F7** | Governance: ISO/IEC 42001 mapping + FRIA (Art. 27) + Art. 12 logs | ⏳ |
| **F8** | Dashboard (Next.js) + polish + demo | ⏳ |

> **Bundle schema note (F1 design constraint):** effective dates are stored
> **per obligation**, not as a single global date — so F2 can add the Omnibus
> scenario *additively* without migrating the format or rewriting golden vectors.

---

## Classifier (F1)

The classification *decision* is a rule engine over a versioned bundle — no LLM,
no randomness, no clock — so the same input and bundle always yield the same
output, with a content-addressed `checksum` an auditor can reproduce.

```python
from attestor.classifier import SystemProfile, classify, load_bundle

bundle = load_bundle("v2026-08")            # legal-text scenario
profile = SystemProfile(role="provider", annex_iii_area="employment")
result = classify(profile, bundle)

result.risk                                  # RiskTier.high
result.effective_dates["art9_risk_management"]   # "2026-08-02"
result.checksum                              # sha256 over canonical(input + bundle + result)
```

**How it works.** A bundle holds (1) `risk_tier_rules` evaluated in order —
*order is precedence* — to pick the headline tier; (2) `obligation_rules` that
each emit one obligation *with its own effective date on the rule* (so the same
article can become applicable on different dates via different pathways, e.g.
Annex III `2026-08-02` vs Annex I embedded `2027-08-02`); and (3) an `articles`
index every obligation reference must resolve in (the contract the F3 citation
validator relies on). GPAI (Arts 51–55) is a **transversal** track, not a fourth
tier — it can coexist with any risk tier.

### F1 scope & simplifications (deliberate, documented)

- **No Art. 6(3) derogation.** The `high_annex_iii` rule treats **every** Annex III
  system as high-risk; it does **not** yet apply the Art. 6(3) filter (an Annex III
  system that does not pose a significant risk of harm is not high-risk). The rule
  ordering is precedence-based, so a future `high_risk_derogation_6_3` rule can be
  inserted **above** `high_annex_iii` without touching anything below it.
- **Art. 49 registration** is modelled for all Annex III provider systems without
  the point-2 / Art. 6(3) refinements.
- **`content_lifecycle`** (new vs legacy synthetic content) is captured on the
  input but is **date-neutral** in F1: under the pure legal text all of Art. 50 is
  `2026-08-02`. The legacy-marking transition (`2026-12-02`) is a Digital Omnibus
  delta and lands in F2.

---

## Stack

| Layer | Technology |
|-------|------------|
| Classifier | Python deterministic rule engine (no LLM in the decision), versioned YAML/JSON bundle |
| Annex IV | LLM **for drafting only**, with citations validated against the bundle |
| C2PA | `c2pa-python` (`Builder` to sign, `Reader` to verify) |
| C2PA keys | KMS/HSM (AWS KMS) in production; local file in dev |
| Timestamp | RFC3161 TSA (AdES "T" level) |
| Ledger | Ed25519 (`cryptography`) + custom Merkle tree + RFC3161 |
| Backend | FastAPI + PostgreSQL (multi-tenant RLS) |
| Frontend | Next.js (registration, compliance dashboard, verifier) |
| PDF | Annex IV dossier + evidence export |

---

## Honesty / scope

This is a **portfolio project**, built to demonstrate engineering across AI
governance, cryptography, and compliance. Read these limits as features, not
disclaimers — knowing them is the difference between a junior and a senior take:

- **Not legal advice.** Attestor is compliance *support and evidence*, designed
  for **human review**. Regulatory interpretation lives in a *versioned bundle*,
  not hardcoded, and anything provisional is flagged as such.
- **The Digital Omnibus is provisional.** As of June 2026 it is a *political
  agreement* **pending formal adoption** (Parliament + Council + publication in
  the OJEU). The **binding legal text is still 2 Aug 2026**; Attestor surfaces
  both the legal-text date and the Omnibus scenario, clearly labelled.
- **C2PA proves provenance, not truth.** A valid Content Credential shows the
  manifest is intact and the signer is trusted — it does **not** assert the
  content is accurate. And the **absence** of a credential does **not** mean
  content was AI-generated.

---

## License

[MIT](LICENSE) © 2026 Marcos Mata García
