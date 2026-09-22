# Attestor

> **Status: `pre-alpha`.** F0–F8 complete: deterministic classifier, Annex IV dossier,
> C2PA provenance, governance views, an offline-verifiable ledger, and a Next.js dashboard.

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

## Verify it in 60 seconds

No keys, no network, no guessing. From a clean clone:

```bash
pip install -e .

# 1. A third party verifies the committed ledger offline
attestor ledger verify examples/ledger
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid); no timestamp
# exit 0

# 2. Tamper with one byte and the verdict flips
sed -i 's/sys-1/sys-9/' examples/ledger/records.json
attestor ledger verify examples/ledger
# ledger TAMPERED - integrity_ok=False, signature_ok=True
# exit 1
git checkout examples/ledger/records.json

# 3. Reproduce a classification checksum, under any scenario
attestor classify --role provider --annex-iii-area employment --checksum-only
# d821e3e0b95d4edda4416916f2a5b02ef0296f34704a0010ee0222b3a9e0ee48   (law in force)
attestor classify --role provider --annex-iii-area employment --bundle v2026-08 --checksum-only
# 15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17   (as enacted)

# 4. The whole pipeline end to end
attestor demo
```

Step 2 is the one worth pausing on: `integrity_ok` goes false while `signature_ok`
stays true. The signature covers the sealed Merkle root, so an edited record says
*the evidence was changed after sealing* - a different accusation from *the
signature is wrong*.

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

## Classifier (F1)

The classification *decision* is a rule engine over a versioned bundle — no LLM,
no randomness, no clock — so the same input and bundle always yield the same
output, with a content-addressed `checksum` an auditor can reproduce.

```python
from attestor.classifier import SystemProfile, classify, load_bundle

bundle = load_bundle("v2026-08")  # legal-text scenario
profile = SystemProfile(role="provider", annex_iii_area="employment")
result = classify(profile, bundle)

result.risk  # RiskTier.high
result.effective_dates["art9_risk_management"]  # "2026-08-02"
result.checksum  # sha256 over canonical(input + bundle + result)
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

## Dual scenario — as enacted vs as amended (F2)

Attestor does not silently swap one timeline for another — it shows **both**.
`compare_timelines` classifies one profile under each bundle and reports, per
obligation, the date under the Regulation as originally enacted and the date under
the Regulation as it binds today.

```python
from attestor.classifier import SystemProfile, compare_timelines

cmp = compare_timelines(SystemProfile(role="provider", annex_iii_area="employment"))
cmp.legal_text_risk  # high
[(o.reference, str(o.legal_text_date), str(o.omnibus_date)) for o in cmp.divergences]
# e.g. ("Art. 9", "2026-08-02", "2027-12-02") — high-risk deferred 16 months
cmp.omnibus_status  # the status caveat, read from the binding bundle meta
```

Each scenario bundle is a **complete, self-contained, content-hashable** unit (not a
diff), carrying only four deltas vs the text as enacted: Annex III high-risk →
`2027-12-02`, Annex I embedded → `2028-08-02`, the Art. 50(2) new/legacy marking
split, and a **new Art. 5 prohibition** (NCII/nudifiers + CSAM, `2026-12-02`, with a
safe harbour). The status caveat lives only in the bundle's `meta.status_note`
(single source of truth) — `compare_timelines` reads it, never hardcodes it.

**That design was tested by reality.** Those four deltas were modelled on 23 June
2026, while the Omnibus was a proposal. It became law on 27 July 2026, all four
matched, and absorbing it cost one new bundle file and one changed default — no
migration, no engine change, no rewritten golden vector. Because effective dates
live **on each obligation** rather than as one global date on the bundle, an
amendment that moves some dates and not others is additive by construction.

---

## Annex IV technical-documentation dossier (F3)

The dossier is a **traceable scaffold generated from the classification** — not
free text. Every structured citation is the `reference` of an obligation the
classifier emitted; nothing is asserted.

```python
from attestor.annexiv import generate_dossier, validate_citations, render_pdf
from attestor.classifier import SystemProfile, classify, load_bundle

bundle = load_bundle("v2026-08")
profile = SystemProfile(role="provider", annex_iii_area="employment")
dossier = generate_dossier(profile, classify(profile, bundle), bundle)

validate_citations(dossier, classify(profile, bundle), bundle)  # fail-closed, or raises
pdf_bytes = render_pdf(dossier)  # deterministic (reportlab)
```

- **Provider-only, high-risk only.** Annex IV is a provider obligation (Art. 11);
  the generator rejects deployers and non-high-risk systems with a specific error.
- **Fail-closed validator, 3 checks:** every citation (a) resolves to an article in
  the bundle, (b) traces to a classifier obligation (no orphans), and (c) together
  cover every classification obligation (completeness). Each has its own message.
- **Deterministic:** same profile + classification + bundle → identical dossier
  model (pinned by golden vectors); the PDF renders byte-identically via reportlab's
  invariant mode.

### What "validated" means, and what this is not (honesty)

- **"Validated"** means the citation *resolves to the bundle* **and** *traces to an
  obligation the classifier emitted* — **not** that the article substantiates an
  arbitrary claim.
- The dossier is a **scaffold**: it tells you which Annex IV sections to complete
  and which obligations/articles/dates apply. It does **not** write your technical
  documentation (that needs real system data → sections carry explicit placeholders).
- The **obligation → section placement is a defensible structuring** based on what
  each Annex IV point covers — **not** a mapping the Regulation prescribes.
- The bundle models a **representative subset** of the high-risk obligations, not the
  exhaustive list: e.g. Section 9 (Art. 72 post-market monitoring) is guidance with no
  derived citation, and Arts 18/19/20 are not yet modelled.

---

## Stack

| Layer | Technology |
|-------|------------|
| Classifier | Python deterministic rule engine (no LLM in the decision), versioned YAML/JSON bundle |
| Annex IV | Deterministic template derived from the classification, no LLM. Citations validated against the bundle |
| C2PA | `c2pa-python` (`Builder` to sign, `Reader` to verify) |
| C2PA keys | Local PEM chain + key, read from config. `Signer.from_callback` is the seam a KMS/HSM signer would plug into; no KMS backend ships here |
| Timestamp | RFC3161 codec (request + token parsing). The token is verified to *bind* to the signed root; TSA chain validation is out of scope |
| Ledger | Ed25519 (`cryptography`) + custom Merkle tree + RFC3161 |
| Backend | FastAPI. No database: nothing in the engine persists state |
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
- **The Digital Omnibus is in force.** Regulation (EU) 2026/1744 was adopted by the
  Council on **29 June 2026** and **entered into force on 27 July 2026**, amending
  Reg. (EU) 2024/1689: Annex III high-risk moves to **2 Dec 2027**, Annex I embedded
  to **2 Aug 2028**. Attestor still shows **both** timelines, because knowing what
  changed is part of the answer: bundle `v2026-08` is the Regulation as originally
  enacted, and bundle `reg-2026-1744` is the binding timeline today (and the
  default). The bundle `omnibus-2026`, modelled on 23 June 2026 while the Omnibus
  was still a proposal, is kept **frozen**: its four deltas matched the adopted
  text, and absorbing the adoption required no change to a single golden vector.
  See [`docs/regulatory-changelog.md`](docs/regulatory-changelog.md), and
  `pytest tests/test_regulatory_evolution.py` to check it.
- **C2PA proves provenance, not truth.** A valid Content Credential shows the
  manifest is intact and the signer is trusted — it does **not** assert the
  content is accurate. And the **absence** of a credential does **not** mean
  content was AI-generated.

---

## License

[MIT](LICENSE) © 2026 Marcos Mata García
