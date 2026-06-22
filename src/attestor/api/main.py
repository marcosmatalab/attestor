"""FastAPI application entrypoint.

F0 scaffold: exposes only a health probe. No business logic yet — the classifier,
Annex IV generator, C2PA provenance, and ledger arrive in later phases.
"""

from fastapi import FastAPI

from attestor import __version__
from attestor.config import settings

app = FastAPI(
    title="Attestor",
    version=__version__,
    description="Deterministic EU AI Act compliance engine (pre-alpha scaffold).",
)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Reports service identity, version, and environment."""
    return {
        "status": "ok",
        "service": "attestor",
        "version": __version__,
        "environment": settings.app_env,
    }
