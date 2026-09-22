"""The C2PA manifest, derived from a classification — never free text.

Same discipline as the Annex IV dossier: what goes into the Content Credential is
what the deterministic engine already decided. The assertion carries the
classification checksum and the bundle hash, so a verifier can take a signed asset
and re-run the classification to confirm the credential describes *this* decision.
"""

from typing import Any

from attestor.classifier.model import Classification

CLAIM_GENERATOR = "attestor"
ATTESTOR_ASSERTION_LABEL = "eu.attestor.classification"
# IPTC digital source type for content produced by a generative model.
TRAINED_ALGORITHMIC_MEDIA = "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia"


def build_manifest(
    classification: Classification,
    *,
    title: str,
    format: str = "image/png",
    version: str,
) -> dict[str, Any]:
    """Build the manifest definition for an asset classified by ``classification``."""
    return {
        "claim_generator_info": [{"name": CLAIM_GENERATOR, "version": version}],
        "title": title,
        "format": format,
        "assertions": [
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.created",
                            # Omitting this makes the action malformed and the whole
                            # manifest invalid, which is easy to ship by accident.
                            "digitalSourceType": TRAINED_ALGORITHMIC_MEDIA,
                        }
                    ]
                },
            },
            {
                "label": ATTESTOR_ASSERTION_LABEL,
                "data": {
                    "regulation": "Reg. (EU) 2024/1689",
                    "risk": classification.risk.value,
                    "bundle_version": classification.bundle_version,
                    "bundle_sha256": classification.bundle_sha256,
                    "classification_checksum": classification.checksum,
                    "obligations": [
                        {
                            "id": o.id,
                            "reference": o.reference,
                            "effective_date": o.effective_date.isoformat(),
                        }
                        for o in classification.obligations
                    ],
                },
            },
        ],
    }
