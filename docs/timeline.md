# Dual scenario: as enacted vs as amended (F2)


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

---

The full history of the bundles is in
[`regulatory-changelog.md`](regulatory-changelog.md).
