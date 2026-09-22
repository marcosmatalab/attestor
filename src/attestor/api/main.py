"""FastAPI application entrypoint.

Wires the health probe and the ``/api`` router. All compliance logic lives in the
engine packages; this module only composes them into an app.
"""

from fastapi import FastAPI

from attestor import __version__
from attestor.api.routes import router
from attestor.config import settings

app = FastAPI(
    title="Attestor",
    version=__version__,
    description="Deterministic EU AI Act compliance engine.",
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
