# The deterministic classifier (F1)

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

See also [`regulatory-changelog.md`](regulatory-changelog.md) for how the bundles
relate to each other, and [`annex-iv.md`](annex-iv.md) for what the classification
feeds into.
