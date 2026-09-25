# Regulatory changelog

Attestor versions *the law*, not just the code. Each bundle is a complete,
content-addressed interpretation of the Regulation at a point in time. Bundles are
never edited: a change in the law is a new bundle, because the ledger anchors
bundle digests and rewriting an anchored artifact is precisely what an evidence
system must not do.

## The bundles

| Bundle | What it is | `sha256` | Status |
|---|---|---|---|
| `v2026-08` | Regulation (EU) 2024/1689 **as originally enacted** | `7e77bc07…3312d49d` | Frozen, historical |
| `omnibus-2026` | The Digital Omnibus on AI **as modelled on 23 June 2026**, while it was still a proposal | `a52cb5e1…99462c51` | Frozen, historical |
| `reg-2026-1744` | Reg. (EU) 2024/1689 **as amended by Reg. (EU) 2026/1744** | `6a8cba0a…563f2c1a` | **In force, and the default** |

Print them yourself:

```bash
python -c "from attestor.classifier import load_bundle as L;   print(*[(v, L(v).sha256) for v in ('v2026-08','omnibus-2026','reg-2026-1744')], sep='
')"
```

## Timeline of the change

| Date | Event |
|---|---|
| 2024-07-12 | Regulation (EU) 2024/1689 (the AI Act) published in the OJEU |
| 2025-11 | European Commission proposes the Digital Omnibus package |
| 2026-05-07 | Provisional political agreement between the co-legislators |
| 2026-06-16 | European Parliament adopts the Digital Omnibus on AI |
| **2026-06-23** | **Bundle `omnibus-2026` written**, modelling the proposal as provisional |
| 2026-06-29 | Council gives its final green light |
| 2026-07-08 | Final act signed |
| 2026-07-24 | Published in the OJEU as **Regulation (EU) 2026/1744** |
| **2026-07-27** | **Enters into force.** |
| **2026-09-22** | **Bundle `reg-2026-1744` added** (commit `00a566d`); it becomes the default in the engine and the API |

## What the amendment changed

Four deltas against the Regulation as originally enacted:

1. **Annex III high-risk** (stand-alone systems, Art. 6(2)): `2026-08-02` → `2027-12-02`.
2. **Annex I embedded high-risk** (Art. 6(1)): `2027-08-02` → `2028-08-02`.
3. **Art. 50(2) marking of synthetic content**: split by content lifecycle — newly
   generated content `2026-08-02`, pre-existing (legacy) content `2026-12-02`. The
   original text did not branch.
4. **Art. 5**: a new prohibition on AI systems generating non-consensual intimate
   imagery (nudifiers) and CSAM, from `2026-12-02`, with a safe harbour where the
   system has adequate technical safeguards.

## The part worth reading

The four deltas above were modelled on **23 June 2026, before the text was adopted**.
When it became law on 27 July 2026, all four turned out to match the adopted text.
The repository absorbed it on **22 September 2026**, in commit `00a566d`:

- **added** the `reg-2026-1744` bundle, and made it the default in `classifier/bundle.py`
  and in the API (both previously `v2026-08`);
- **changed** `classifier/timeline.py` so the comparison runs against the bundle in force
  rather than the provisional overlay;
- **renamed** the Annex IV field `provisional_note` to `status_note` (`annexiv/model.py`,
  `generator.py`, `pdf.py`), because once the Omnibus was law the old name would have made
  a dossier state the opposite of the truth; `tests/golden/annexiv-v2026-08.yaml` follows
  the rename.

No rule was migrated. No earlier bundle moved by a byte, and neither did the
classification golden vectors of `v2026-08` and `omnibus-2026`
(`git show --stat 00a566d` lists neither).

That is not luck, it is a schema decision: effective dates are stored **on each
obligation**, never as a single global date on the bundle. A global date would have
forced a migration and a rewrite of every golden vector the first time one
obligation moved and another did not — which is exactly what the Omnibus did.

`tests/test_regulatory_evolution.py` holds that claim to account. It asserts the two
historical digests as typed literals, and checks vector by vector that the dates
modelled as a proposal are the dates that became law. If anyone edits a frozen
bundle, the build fails before the artifact ships.

## Sources

- [Council of the EU, final green light, 29 June 2026](https://www.consilium.europa.eu/en/press/press-releases/2026/06/29/artificial-intelligence-council-gives-final-green-light-to-simplify-and-streamline-rules/)
- [Regulation (EU) 2026/1744, EUR-Lex](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng)
- [White & Case, what the Omnibus amends in the AI Act](https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act)
- [Hunton, EU Digital Omnibus on AI enters into force](https://www.hunton.com/privacy-and-cybersecurity-law-blog/eu-digital-omnibus-on-ai-enters-into-force)

The OJEU text is what governs; the commentary above is orientation, not authority.
