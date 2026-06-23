"""C2PA content provenance: sign AI outputs with verifiable Content Credentials.

F4 covers SIGNING only (verification and the trust nuance are F5). Signing serves
the Art. 50 transparency obligation by marking AI-generated content, but C2PA is a
provenance/integrity signal, not proof of truth — see the README honesty note.
"""

from attestor.provenance.devcert import generate_dev_cert
from attestor.provenance.manifest import ProvenanceMetadata, build_manifest
from attestor.provenance.signer import SignerConfig, build_signer, sign_asset

__all__ = [
    "ProvenanceMetadata",
    "SignerConfig",
    "build_manifest",
    "build_signer",
    "generate_dev_cert",
    "sign_asset",
]
