"""Development signing material: a self-signed X.509 chain for C2PA.

This exists so the repo signs and verifies with **no keys and no network** — a
reviewer runs the demo on a clean clone and gets a real Content Credential, not a
mock. The trade-off is stated everywhere it matters: a self-signed chain is not on
any C2PA trust list, so the verifier reports the signer as UNTRUSTED, which is the
truthful answer and the one the README shows.

The C2PA certificate profile is narrow, and two of its requirements are easy to
miss (both cost a "the certificate is invalid" signing failure): the end-entity
certificate needs an extended key usage of ``emailProtection`` or
``documentSigning``, and it needs subject/authority key identifiers.
"""

import datetime
from dataclasses import dataclass
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from attestor.config import settings

_NOT_BEFORE = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
_NOT_AFTER = datetime.datetime(2036, 1, 1, tzinfo=datetime.UTC)


@dataclass(frozen=True)
class SigningMaterial:
    """A leaf private key plus the PEM chain that certifies it."""

    private_key: ec.EllipticCurvePrivateKey
    certificate_chain_pem: str
    root_pem: str

    @property
    def private_key_pem(self) -> str:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("ascii")


def _name(common_name: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "ES"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Attestor (development)"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ]
    )


def generate_dev_signing_material() -> SigningMaterial:
    """Generate a fresh self-signed root plus an ES256 leaf that C2PA will accept."""
    root_key = ec.generate_private_key(ec.SECP256R1())
    root_subject = _name("Attestor Development Root CA")
    root = (
        x509.CertificateBuilder()
        .subject_name(root_subject)
        .issuer_name(root_subject)
        .public_key(root_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_NOT_BEFORE)
        .not_valid_after(_NOT_AFTER)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(root_key.public_key()), False)
        .sign(root_key, hashes.SHA256())
    )

    leaf_key = ec.generate_private_key(ec.SECP256R1())
    leaf = (
        x509.CertificateBuilder()
        .subject_name(_name("Attestor Development Signer"))
        .issuer_name(root.subject)
        .public_key(leaf_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(_NOT_BEFORE)
        .not_valid_after(_NOT_AFTER)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        # Required by the C2PA certificate profile.
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]), False)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()), False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()), False
        )
        .sign(root_key, hashes.SHA256())
    )

    leaf_pem = leaf.public_bytes(serialization.Encoding.PEM).decode("ascii")
    root_pem = root.public_bytes(serialization.Encoding.PEM).decode("ascii")
    return SigningMaterial(
        private_key=leaf_key,
        certificate_chain_pem=leaf_pem + root_pem,
        root_pem=root_pem,
    )


def load_signing_material(cert_path: str | Path, key_path: str | Path) -> SigningMaterial:
    """Load a PEM certificate chain and its EC private key from disk."""
    chain = Path(cert_path).read_text(encoding="ascii")
    key = serialization.load_pem_private_key(Path(key_path).read_bytes(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey):
        raise ValueError(
            f"{key_path} is not an EC private key: {type(key).__name__}. "
            "C2PA ES256 signing needs a P-256 key."
        )
    return SigningMaterial(private_key=key, certificate_chain_pem=chain, root_pem="")


def signing_material_from_settings() -> SigningMaterial:
    """Use the configured PEM material if both paths are set, else mint dev material.

    This is the seam. Replacing the loader with one that talks to a KMS is the whole
    change a KMS integration would need; no such backend is implemented here.
    """
    cert_path = settings.c2pa_cert_path
    key_path = settings.c2pa_private_key_path
    if cert_path and key_path:
        return load_signing_material(cert_path, key_path)
    return generate_dev_signing_material()
