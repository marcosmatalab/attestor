"""Config-driven C2PA signer.

Signs an asset with a C2PA manifest using a certificate chain + private key taken
from config (never hardcoded). The signer is built via ``Signer.from_callback`` —
the same interface a KMS/HSM-backed signer uses (the key signs inside the
callback), so dev and production share one code path. An optional RFC3161 TSA URL
adds a trusted timestamp (AdES "T"); without it, signing is fully offline. ES256
(EC P-256) only in F4.
"""

import io
import json
from pathlib import Path

import c2pa
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from pydantic import BaseModel, ConfigDict

from attestor.config import Settings
from attestor.provenance.manifest import ProvenanceMetadata, build_manifest

_ES256_COORD_BYTES = 32  # P-256: r and s are 32 bytes each (raw COSE signature)


class SignerConfig(BaseModel):
    """Where the signing certificate chain and key live, plus an optional TSA."""

    model_config = ConfigDict(frozen=True)

    cert_path: str
    private_key_path: str
    tsa_url: str | None = None

    @classmethod
    def from_settings(cls, settings: Settings) -> "SignerConfig":
        if not settings.c2pa_cert_path or not settings.c2pa_private_key_path:
            raise ValueError(
                "C2PA signing is not configured: set C2PA_CERT_PATH and "
                "C2PA_PRIVATE_KEY_PATH (generate a dev cert with generate_dev_cert)"
            )
        return cls(
            cert_path=settings.c2pa_cert_path,
            private_key_path=settings.c2pa_private_key_path,
            tsa_url=settings.rfc3161_tsa_url,
        )


def build_signer(config: SignerConfig) -> c2pa.Signer:
    """Build a C2PA signer from the configured certificate chain and key."""
    cert_chain = _read(config.cert_path, "certificate")
    key_pem = _read(config.private_key_path, "private key")
    private_key = serialization.load_pem_private_key(key_pem, password=None)
    if not isinstance(private_key, ec.EllipticCurvePrivateKey):
        raise ValueError("C2PA signer requires an EC P-256 private key (ES256)")

    def sign_es256(data: bytes) -> bytes:
        der = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(der)
        return r.to_bytes(_ES256_COORD_BYTES, "big") + s.to_bytes(_ES256_COORD_BYTES, "big")

    return c2pa.Signer.from_callback(
        sign_es256, c2pa.C2paSigningAlg.ES256, cert_chain.decode("utf-8"), config.tsa_url
    )


def sign_asset(
    source_path: str | Path,
    dest_path: str | Path,
    config: SignerConfig,
    metadata: ProvenanceMetadata,
) -> bytes:
    """Sign the asset at ``source_path`` into ``dest_path``; return the manifest bytes."""
    signer = build_signer(config)
    builder = c2pa.Builder(json.dumps(build_manifest(metadata)))
    source = io.BytesIO(Path(source_path).read_bytes())
    dest = io.BytesIO()
    manifest_bytes = builder.sign(signer, metadata.format, source, dest)
    Path(dest_path).write_bytes(dest.getvalue())
    return manifest_bytes


def _read(path: str | Path, what: str) -> bytes:
    resolved = Path(path)
    if not resolved.is_file():
        raise ValueError(f"C2PA signing {what} not found at {resolved}")
    return resolved.read_bytes()
