# Governance views (F7)

Three re-presentations of what the classifier already decided, each answering a
question a different reader actually asks. **None of them re-decides applicability**:
they read the `Classification`, so there is one source of truth and the dates come
from the same per-obligation values everything else uses.

```python
from attestor.governance import assess_fria, log_retention_duties, map_to_iso42001
```

## ISO/IEC 42001 map

An organisation that already runs an AI management system does not want a second,
parallel compliance programme. Mapping each emitted obligation onto the 42001 clause
that already owns it turns "23 articles" into "the clauses you are already audited
against, plus these gaps".

```python
mapping = map_to_iso42001(classification)
mapping.clauses  # ('4.4', '5.3', '6.1', '7.5', '8.1', '9.2', 'A.6.2.4', ...)
mapping.unmapped_obligations  # reported, never silently dropped
```

**This mapping is a defensible structuring, not a normative correspondence.**
ISO/IEC 42001 is a management-system standard and the AI Act is law; neither
declares the other's mapping. It is kept as data in one table so it can be argued
with, every entry carries a written rationale, and a test asserts that every
obligation is either mapped or listed as unmapped - the view can never look more
complete than it is.

## FRIA (Art. 27)

```python
fria = assess_fria(classification)
fria.required  # True only when the classifier emitted art27_fria
fria.effective_date  # the obligation's own date
fria.elements  # the six elements of Art. 27(1)(a)-(f)
```

Applicability is **not** recomputed here. Art. 27 is already an obligation the
bundle rules emit, for deployers that are public bodies or private entities
providing public services, using an Annex III system other than point 2. This module
reads that decision and adds the scaffold. Like the Annex IV dossier, it tells you
what to write; it does not write it.

## Record-keeping (Art. 12 and Art. 26(6))

Two separate duties on separate parties, routinely conflated:

- **Art. 12** obliges the *provider* to design automatic logging into the system.
- **Art. 26(6)** obliges the *deployer* to keep the logs it generates, for at least
  six months unless other Union or national law provides otherwise.

Attestor states the six-month floor and says that it is a floor. It deliberately
does **not** compute a retention end date: the actual period depends on sectoral law
the engine does not model, and inventing a date would be the kind of confident wrong
answer this project exists to avoid.
