"""Fail-closed citation validator for the Annex IV dossier.

Three independent checks, each with a specific message. A dossier is only valid if
every derived citation (a) resolves to an article in the bundle, (b) traces to an
obligation the classifier emitted (no orphan citations), and (c) together they
cover every classification obligation (completeness). Anything else raises.
"""

from attestor.annexiv.model import AnnexIVDossier
from attestor.classifier.bundle import Bundle
from attestor.classifier.model import Classification


class CitationError(ValueError):
    """Raised when a dossier's citations are not fully resolvable and traceable."""


def validate_citations(
    dossier: AnnexIVDossier, classification: Classification, bundle: Bundle
) -> None:
    """Validate the dossier's citations against the classification and bundle."""
    classification_ids = {o.id for o in classification.obligations}
    cited_ids: set[str] = set()

    for citation in dossier.all_citations:
        # (a) the reference must resolve in the bundle's article index
        if citation.reference not in bundle.articles:
            raise CitationError(
                f"unresolved citation: {citation.reference!r} "
                f"(obligation {citation.obligation_id!r}) is not in the bundle article index"
            )
        # (b) no orphan: the cited obligation must have been emitted by the classifier
        if citation.obligation_id not in classification_ids:
            raise CitationError(
                f"orphan citation: obligation {citation.obligation_id!r} "
                "was not emitted by the classifier"
            )
        cited_ids.add(citation.obligation_id)

    # (c) completeness: every classification obligation must be cited somewhere
    missing = classification_ids - cited_ids
    if missing:
        raise CitationError(
            f"incomplete dossier: classification obligations not cited: {sorted(missing)}"
        )
