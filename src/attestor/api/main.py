"""FastAPI application entrypoint.

The HTTP layer is a THIN wrapper over the deterministic engine: ``/api`` routes (F8) call
the classifier, Annex IV generator, C2PA verifier, and ledger and return their output
verbatim. No compliance logic lives here — see :mod:`attestor.api.routes`.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from attestor import __version__
from attestor.api.routes import router
from attestor.config import settings

app = FastAPI(
    title="Attestor",
    version=__version__,
    description="Deterministic EU AI Act compliance engine (portfolio demonstration).",
)

# Allow the local Next.js dev server to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness probe. Reports service identity, version, and environment."""
    return {
        "status": "ok",
        "service": "attestor",
        "version": __version__,
        "environment": settings.app_env,
    }
