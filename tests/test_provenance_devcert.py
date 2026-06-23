"""Tests for the development certificate chain generator."""

from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509.oid import ExtendedKeyUsageOID

from attestor.provenance import generate_dev_cert


def test_generate_dev_cert_writes_a_leaf_plus_ca_chain(tmp_path: Path) -> None:
    cert_path = tmp_path / "chain.pem"
    key_path = tmp_path / "key.pem"
    generate_dev_cert(cert_path, key_path)

    assert cert_path.exists()
    assert key_path.exists()

    certs = x509.load_pem_x509_certificates(cert_path.read_bytes())
    assert len(certs) == 2  # leaf + CA
    leaf, ca = certs

    # Leaf carries the C2PA end-entity profile.
    assert leaf.extensions.get_extension_for_class(x509.BasicConstraints).value.ca is False
    assert leaf.extensions.get_extension_for_class(x509.KeyUsage).value.digital_signature
    eku = leaf.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value
    assert ExtendedKeyUsageOID.EMAIL_PROTECTION in eku

    # CA is a CA, and the leaf is issued by it.
    assert ca.extensions.get_extension_for_class(x509.BasicConstraints).value.ca is True
    assert leaf.issuer == ca.subject


def test_private_key_is_ec_p256(tmp_path: Path) -> None:
    cert_path = tmp_path / "chain.pem"
    key_path = tmp_path / "key.pem"
    generate_dev_cert(cert_path, key_path)

    key = load_pem_private_key(key_path.read_bytes(), password=None)
    assert isinstance(key, ec.EllipticCurvePrivateKey)
    assert key.curve.name == "secp256r1"
