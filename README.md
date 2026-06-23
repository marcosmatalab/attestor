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
| **F2** | **Additive:** Omnibus-scenario bundle + timeline resolution presenting **both** dates (legal text vs Omnibus provisional) + the "pending formal adoption" caveat. *No rewrite of F1 goldens.* | ✅ |
| **F3** | Annex IV generator + **validated citations** (a citation that doesn't resolve is rejected) + PDF export | ✅ |
| **F4** | C2PA signer — manifest (X.509) + RFC3161 timestamp, keys via KMS/HSM | ✅ |
| **F5** | C2PA verifier — reports signer + assertions + the provenance **nuance** | ⏳ |
| **F6** | Ledger Ed25519 + Merkle + RFC3161, **offline** verification via CLI | ✅ |
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

## Dual scenario — legal text vs Digital Omnibus (F2)

F2 does **not** replace the binding legal text with the Omnibus — it shows **both**.
`compare_timelines` classifies one profile under each bundle and reports, per
obligation, the legal-text date vs the Omnibus date.

```python
from attestor.classifier import SystemProfile, compare_timelines

cmp = compare_timelines(SystemProfile(role="provider", annex_iii_area="employment"))
cmp.legal_text_risk            # high
[(o.reference, str(o.legal_text_date), str(o.omnibus_date)) for o in cmp.divergences]
# e.g. ("Art. 9", "2026-08-02", "2027-12-02") — high-risk deferred 16 months
cmp.omnibus_status             # the provisional caveat, read from the bundle meta
```

The Omnibus bundle (`omnibus-2026`) is a **complete, self-contained, content-hashable**
unit (not a diff), carrying only four deltas vs the legal text: Annex III high-risk
→ `2027-12-02`, Annex I embedded → `2028-08-02`, the Art. 50(2) new/legacy marking
split, and a **new Art. 5 prohibition** (NCII/nudifiers + CSAM, `2026-12-02`, with a
safe harbour). The provisional caveat lives only in the bundle's `meta.status_note`
(single source of truth) — `compare_timelines` reads it, never hardcodes it.

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

validate_citations(dossier, classify(profile, bundle), bundle)   # fail-closed, or raises
pdf_bytes = render_pdf(dossier)                                   # deterministic (reportlab)
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

## C2PA content provenance — signer (F4)

Signs an AI output with a C2PA manifest (Content Credentials) carrying an
AI-generated marking (`c2pa.actions.v2` + the IPTC `trainedAlgorithmicMedia`
source type) and an Attestor disclosure assertion. Built on `c2pa-python==0.36.0`.

```python
from attestor.provenance import ProvenanceMetadata, SignerConfig, generate_dev_cert, sign_asset

generate_dev_cert("dev_chain.pem", "dev_key.pem")          # dev only — never commit
config = SignerConfig(cert_path="dev_chain.pem", private_key_path="dev_key.pem")
sign_asset("input.png", "signed.png", config,
           ProvenanceMetadata(title="input.png", model="claude-opus-4-8"))
```

- **Signing via `Signer.from_callback`** — the same interface a KMS/HSM signer
  uses (the key signs inside a callback), so dev (local key) and production (KMS)
  share one code path. ES256 (EC P-256).
- **RFC3161 timestamp** is optional (`RFC3161_TSA_URL`): when set, the TSA
  countersignature gives the C2PA claim an AdES "T"-level trusted time, linking to
  the F6 ledger. Without it, signing is fully offline.
- **Keys are config-driven**, never hardcoded or committed. The dev certificate is
  a self-signed **leaf + Root CA chain** (c2pa-rs rejects a lone self-signed cert).

### What C2PA proves, and what this is not (honesty)

- **C2PA proves PROVENANCE and INTEGRITY, not truth.** A valid Content Credential
  shows the manifest is intact and identifies the signer — it does **not** assert
  the content is real. **Absence** of a credential does **not** mean AI-generated;
  **presence** does not mean the content is authentic.
- **C2PA does not require declaring AI origin.** A validly signed asset may omit the
  `digitalSourceType` entirely. Attestor *chooses* to include the disclosure (in
  service of **Art. 50** of Reg. (EU) 2024/1689) — its presence is Attestor's choice,
  not something C2PA imposes.
- **The dev signer is an untrusted, self-signed certificate** — **not** on any C2PA
  trust list. A verifier will mark the signer as untrusted; that trust nuance (and
  the verifier itself) is **F5**.

---

## Cryptographic ledger — offline-verifiable (F6)

An **append-only log** of records (a dossier hash, a C2PA manifest hash, …). Each
record is hashed with the **same `canonical.py`** the classifier checksums with, the
leaves form a deterministic **RFC 6962 Merkle tree**, and the root is signed with
**Ed25519**. The signed root can optionally be **timestamped (RFC 3161)**. A third party
verifies everything **offline** — with only public artifacts, no private key and no
network.

```python
from attestor.ledger import Ledger, generate_ledger_key, load_private_key, save_ledger

generate_ledger_key("ledger.key")               # dev only — never commit; prod uses a KMS/HSM
key = load_private_key("ledger.key")

ledger = Ledger()
ledger.append({"type": "dossier", "id": "sys-1", "sha256": "…"})
ledger.append({"type": "c2pa", "id": "img-1", "sha256": "…"})

signed = ledger.seal(key)                        # Merkle root + Ed25519 signature (deterministic)
save_ledger("out/ledger", ledger.records, signed)
```

```bash
# Offline verifier — public artifacts only (records.json, signed_root.json, optional tsa/*.pem)
python -m attestor.ledger out/ledger
# ledger VERIFIED (Merkle root intact, Ed25519 signature valid); timestamped … - TSA UNTRUSTED …
# exit 0 if intact and signed, exit 1 if tampering is detected
```

- **Deterministic.** Same records + same key → same Merkle root and same Ed25519
  signature (RFC 8032). The RFC 3161 token is *not* byte-reproducible (it depends on the
  TSA and the time), so it is verified, never byte-compared.
- **Inclusion proofs.** Given a record, the ledger emits an RFC 6962 audit path so a
  third party can verify membership **without** the whole tree.
- **Offline by construction.** Verification needs the public key, the signed root, the
  records (or an inclusion proof), and — for the timestamp — the TSA certificates. If it
  needed the private key or the network, the "offline" claim would be hollow.

### What the ledger proves, and what this is not (honesty)

- **It is an append-only log with cryptographic integrity — NOT a blockchain.** There is
  no distribution and no consensus; the operator holds the signing key. It gives
  third parties offline-verifiable integrity and existence evidence, nothing more.
- **The value, and its limit.** Once a root is **signed *and* timestamped**, altering
  the entries beneath it without detection is infeasible, and its existence at time *T*
  is demonstrable. **But** the operator can still fork or rewrite history that has **not
  yet been anchored** — the security depends on signing, timestamping, and ideally
  publishing roots **regularly**. Anchoring is a discipline, not a one-off.
- **Ed25519 ≠ legal identity.** The signature proves the root was signed by the holder
  of the key (authenticity and integrity of the root), not *who* in any legal sense.
- **RFC 3161 trust is a separate axis.** A timestamp proves existence-in-time **only by
  trusting the TSA**. A free/dev TSA can issue a perfectly valid token yet not be a
  recognised authority — so the verifier reports `tsa_trusted` **separately** and never
  lets an untrusted TSA look like a tampered ledger (the same integrity-vs-trust split as
  C2PA in F5). The exit code is driven by integrity and signature alone.

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
- **The Digital Omnibus is not yet in force.** As of **23 June 2026** the European
  Parliament has approved it (16 Jun 2026), but the Council's **formal adoption is
  still pending** (expected 29 Jun 2026), after which it would be published in the
  OJEU and enter into force. The **binding legal text remains Reg. (EU) 2024/1689**
  (2 Aug 2026 timeline); Attestor surfaces both scenarios, with the Omnibus clearly
  marked provisional (the live caveat lives in the Omnibus bundle's `meta`).
- **C2PA proves provenance, not truth.** A valid Content Credential shows the
  manifest is intact and the signer is trusted — it does **not** assert the
  content is accurate. And the **absence** of a credential does **not** mean
  content was AI-generated.
- **The ledger is an append-only log, not a blockchain.** It gives third parties
  offline-verifiable integrity and existence proofs, but it is not distributed and has
  no consensus: the operator holds the key and can still rewrite history that has not
  yet been signed and timestamped. Its guarantees follow from anchoring roots regularly,
  and timestamp trust depends on the TSA (reported separately from tampering).

---

## License

[MIT](LICENSE) © 2026 Marcos Mata García
