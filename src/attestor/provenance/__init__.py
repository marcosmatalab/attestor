"""C2PA content provenance: sign AI outputs and verify their Content Credentials.

F4 signs (Art. 50 transparency marking); F5 verifies, separating manifest INTEGRITY
(``validation_state``) from signer TRUST (``signingCredential.*``) — "Valid" never
implies a trusted signer. C2PA is a provenance/integrity signal, not proof of truth —
see the README honesty note.
"""

from attestor.provenance.devcert import generate_dev_cert
from attestor.provenance.manifest import ProvenanceMetadata, build_manifest
from attestor.provenance.signer import SignerConfig, build_signer, sign_asset
from attestor.provenance.verifier import (
    AiDisclosure,
    SignerIdentity,
    ValidationCodes,
    VerificationReport,
    verify_asset,
)

__all__ = [
    "AiDisclosure",
    "ProvenanceMetadata",
    "SignerConfig",
    "SignerIdentity",
    "ValidationCodes",
    "VerificationReport",
    "build_manifest",
    "build_signer",
    "generate_dev_cert",
    "sign_asset",
    "verify_asset",
]
