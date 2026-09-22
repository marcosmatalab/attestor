"""C2PA Content Credentials: sign AI outputs (F4) and verify them (F5).

Provenance proves *where content came from*, not that it is true. This package
keeps that distinction structural rather than editorial: the verifier reports
integrity and trust as two independent axes, so an unrecognised signer can never
be rendered as a tampered file, nor an intact file as an endorsement.
"""

from attestor.provenance.asset import synthetic_png
from attestor.provenance.certs import (
    SigningMaterial,
    generate_dev_signing_material,
    load_signing_material,
    signing_material_from_settings,
)
from attestor.provenance.manifest import build_manifest
from attestor.provenance.signer import build_signer, sign_bytes, sign_file
from attestor.provenance.verifier import ProvenanceReport, verify_bytes

__all__ = [
    "ProvenanceReport",
    "SigningMaterial",
    "build_manifest",
    "build_signer",
    "generate_dev_signing_material",
    "load_signing_material",
    "sign_bytes",
    "sign_file",
    "signing_material_from_settings",
    "synthetic_png",
    "verify_bytes",
]
