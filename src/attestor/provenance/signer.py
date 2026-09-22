"""C2PA signing (F4): manifest (X.509) + optional RFC3161 timestamp.

The signing key never leaves the callback. ``Signer.from_callback`` takes a
``bytes -> bytes`` function, so the private key material is reached through one
narrow seam rather than handed to the C2PA library. That seam is the same
interface a KMS or HSM signer plugs into — swap the callback for one that calls
``kms.sign`` and nothing else in this module changes. **No KMS backend is
implemented here**, and the README says so; what exists is the seam, not the
integration.

The key path is config-driven; a KMS/HSM signer would replace the loader.
"""

from pathlib import Path

from c2pa import Builder, C2paSigningAlg, Signer
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

from attestor.provenance.certs import SigningMaterial


def build_signer(material: SigningMaterial, *, tsa_url: str | None = None) -> Signer:
    """Build a C2PA signer that signs through a callback over ``material``.

    ``tsa_url`` is passed straight to the C2PA SDK, which fetches an RFC3161 token
    at signing time. It is ``None`` by default so the default path stays offline.
    """
    private_key = material.private_key

    def sign_callback(data: bytes) -> bytes:
        # The one place private key material is used. A KMS signer replaces
        # exactly this function body and nothing else.
        return private_key.sign(data, ec.ECDSA(hashes.SHA256()))

    return Signer.from_callback(
        callback=sign_callback,
        alg=C2paSigningAlg.ES256,
        certs=material.certificate_chain_pem,
        tsa_url=tsa_url,
    )


def sign_bytes(
    manifest: dict[str, object],
    source: bytes,
    signer: Signer,
    *,
    format: str = "image/png",
) -> bytes:
    """Sign ``source`` in memory and return the asset with its Content Credential."""
    import io

    builder = Builder(manifest)
    destination = io.BytesIO()
    builder.sign(signer, format, io.BytesIO(source), destination)
    return destination.getvalue()


def sign_file(
    manifest: dict[str, object],
    source: str | Path,
    destination: str | Path,
    signer: Signer,
) -> Path:
    """Sign the asset at ``source``, writing the credentialed asset to ``destination``."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    Builder(manifest).sign_file(str(source), str(target), signer)
    return target
