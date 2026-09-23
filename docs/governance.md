# Governance artifacts (F7)

Three **deterministic** artifacts derived from the classification that **help address**
governance obligations. Read the honesty limits below carefully: none of them is an
audit, certification, completed assessment, or statement of conformity.

```python
from attestor.classifier import SystemProfile, classify, load_bundle
from attestor.governance import (
    Art12Event,
    Art12EventType,
    Art12Log,
    derive_crosswalk,
    generate_fria,
)

bundle = load_bundle("v2026-08")
profile = SystemProfile(role="deployer", deployer_type="public_body", annex_iii_area="employment")
classification = classify(profile, bundle)

crosswalk = derive_crosswalk(classification)  # AI Act obligation → ISO/IEC 42001 clauses + Annex A
fria = generate_fria(
    profile, classification
)  # Art. 27(1)(a)–(f) scaffold (raises if FRIA doesn't apply)

log = Art12Log()
log.record(
    Art12Event(event_type=Art12EventType.risk_situation, occurred_at="2026-08-03T10:00:00+00:00")
)
signed = log.seal(ledger_key)  # tamper-evident, offline-verifiable via the F6 ledger
```

- **ISO/IEC 42001 crosswalk.** For each applied AI Act obligation it points to the related
  ISO/IEC 42001:2023 clauses (4–10) and Annex A control groups (A.2–A.10). A defensible
  design map (like the F3 obligation→section map), built only from obligations actually
  emitted; AI-Act-specific procedures with no clean 42001 analogue are omitted, not stretched.
- **FRIA scaffold (Art. 27).** Derived from a deployer classification, **gated** on the
  classifier's `art27_fria` decision (it raises if the FRIA does not apply). It enumerates
  Art. 27(1)(a)–(f) with explicit `[TO BE COMPLETED]` placeholders.
- **Art. 12 audit log.** Typed events for what Art. 12(2)/(3) require, recorded into the F6
  ledger so the log is tamper-evident and offline-verifiable — altering an event breaks
  verification.

### What these are, and what they are not (honesty)

- **Crosswalk, not audit.** The ISO/IEC 42001 mapping is a **reference crosswalk** to locate
  relevant clauses/controls — **not** an audit, certification, gap assessment, or statement
  of conformity. It cites only clause/control **identifiers** and short group headings; it
  reproduces **no normative text** (ISO/IEC 42001 is a paid standard). The Annex A numbering
  is pinned to ISO/IEC 42001:2023 (A.5–A.10), which several secondary sources get wrong.
- **Scaffold, not a completed FRIA.** Applicability is decided by the classifier, not
  re-litigated here; the output is a structure to be filled in after substantive analysis.
  Generating it neither constitutes nor substitutes for the assessment.
- **Capability, not conformity.** An Art. 12 logging capability is **necessary but not
  sufficient** for Art. 12 conformity. Recording events — even tamper-evidently — does not by
  itself make a system compliant.
