# The Annex IV dossier (F3)

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
