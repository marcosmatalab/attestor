"""Annex IV technical-documentation dossier (Reg. (EU) 2024/1689, Article 11).

The dossier is a traceable scaffold DERIVED from a ``Classification``: every
citation is the ``reference`` of an obligation the deterministic classifier
emitted, never free text. It tells the provider which Annex IV sections to
complete and which obligations/articles/dates apply — it does not write the
technical content (that needs real system data; sections carry placeholders).
"""

from attestor.annexiv.citations import CitationError, validate_citations
from attestor.annexiv.generator import generate_dossier
from attestor.annexiv.model import AnnexIVDossier, Citation, DossierSection

__all__ = [
    "AnnexIVDossier",
    "Citation",
    "CitationError",
    "DossierSection",
    "generate_dossier",
    "validate_citations",
]
