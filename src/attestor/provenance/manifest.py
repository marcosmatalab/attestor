"""C2PA provenance manifest builder (deterministic, no LLM).

Builds the manifest definition Attestor signs into an asset. The AI-generated
marking uses the C2PA v2 actions assertion (``c2pa.actions.v2``) with the IPTC
``digitalSourceType`` for trained algorithmic media, plus a custom Attestor
disclosure assertion. Including the disclosure is Attestor's choice — C2PA does
NOT require declaring AI origin (a validly signed asset may omit it).
"""

from typing import Any

from pydantic import BaseModel, ConfigDict

from attestor import __version__

# IPTC digital source type for AI-generated ("trained algorithmic") media.
TRAINED_ALGORITHMIC_MEDIA = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"


class ProvenanceMetadata(BaseModel):
    """Inputs that parameterise the manifest for one asset."""

    model_config = ConfigDict(frozen=True)

    title: str
    format: str = "image/png"
    ai_generated: bool = True
    model: str | None = None
    claim_generator: str = f"attestor/{__version__}"


def build_manifest(metadata: ProvenanceMetadata) -> dict[str, Any]:
    """Return the C2PA manifest definition for ``metadata``."""
    created_action: dict[str, Any] = {
        "action": "c2pa.created",
        "softwareAgent": {"name": metadata.claim_generator},  # object form (v2)
    }
    if metadata.ai_generated:
        created_action["digitalSourceType"] = TRAINED_ALGORITHMIC_MEDIA

    disclosure: dict[str, Any] = {
        "ai_generated": metadata.ai_generated,
        "eu_ai_act_art50": True,  # Reg. (EU) 2024/1689 Art. 50 (not the old draft Art. 52)
        "generated_by": "attestor",
    }
    if metadata.model is not None:
        disclosure["model"] = metadata.model

    name, _, version = metadata.claim_generator.partition("/")
    return {
        "claim_generator_info": [{"name": name, "version": version or "0"}],
        "title": metadata.title,
        "format": metadata.format,
        "assertions": [
            {"label": "c2pa.actions.v2", "data": {"actions": [created_action]}},
            {"label": "com.attestor.ai_disclosure", "data": disclosure},
        ],
    }
