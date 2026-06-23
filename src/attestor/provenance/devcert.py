"""Self-signed development certificate generator for C2PA signing.

c2pa-rs rejects a lone self-signed certificate: it requires an end-entity (leaf)
signing certificate issued by a CA, carrying the C2PA certificate profile
(KeyUsage digitalSignature, EKU emailProtection, BasicConstraints CA:FALSE). This
mints a dev Root CA plus a leaf signed by it, and writes the PEM chain (leaf + CA)
and the leaf private key.

FOR DEVELOPMENT ONLY. The CA is not on any C2PA trust list, so a verifier will mark
the signer as untrusted (handled in F5). Never commit the generated files.
"""

import datetime
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

_NOT_BEFORE = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)
_NOT_AFTER = datetime.datetime(2034, 1, 1, tzinfo=datetime.UTC)
_PEM = serialization.Encoding.PEM


def generate_dev_cert(cert_chain_path: str | Path, private_key_path: str | Path) -> None:
    """Write a dev PEM certificate chain (leaf + CA) and the leaf private key."""
    ca_key = ec.generate_private_key(ec.SECP256R1())
    ca_cert = _build_ca(ca_key)
    leaf_key = ec.generate_private_key(ec.SECP256R1())
    leaf_cert = _build_leaf(leaf_key, ca_key, ca_cert)

    chain = leaf_cert.public_bytes(_PEM) + ca_cert.public_bytes(_PEM)
    key_pem = leaf_key.private_bytes(
        _PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    Path(cert_chain_path).write_bytes(chain)
    Path(private_key_path).write_bytes(key_pem)


def _name(common_name: str) -> x509.Name:
    return x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Attestor Dev"),
        ]
    )


def _build_ca(ca_key: ec.EllipticCurvePrivateKey) -> x509.Certificate:
    name = _name("Attestor Dev Root CA (untrusted)")
    return (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(ca_key.public_key())
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
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key()), critical=False
        )
        .sign(ca_key, hashes.SHA256())
    )


def _build_leaf(
    leaf_key: ec.EllipticCurvePrivateKey,
    ca_key: ec.EllipticCurvePrivateKey,
    ca_cert: x509.Certificate,
) -> x509.Certificate:
    return (
        x509.CertificateBuilder()
        .subject_name(_name("Attestor Dev Signer (untrusted)"))
        .issuer_name(ca_cert.subject)
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
        .add_extension(
            x509.ExtendedKeyUsage([ExtendedKeyUsageOID.EMAIL_PROTECTION]), critical=False
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(leaf_key.public_key()), critical=False
        )
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()), critical=False
        )
        .sign(ca_key, hashes.SHA256())
    )
