"""Every configuration variable must be read by something.

An unread variable in `.env.example` advertises a capability the project does not
have, which is the same failure as a README claim with no code behind it. This
test is what stops one from creeping back in.
"""

from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.config import Settings, settings
from attestor.ledger.keys import ledger_key_from_settings, public_key_hex, save_ledger_key
from attestor.provenance.certs import (
    generate_dev_signing_material,
    load_signing_material,
    signing_material_from_settings,
)

ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"


def declared_variables() -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }


def test_env_example_declares_exactly_what_settings_reads() -> None:
    assert declared_variables() == {name.upper() for name in Settings.model_fields}


def test_no_ghost_variables_from_abandoned_plans() -> None:
    """DATABASE_URL, AWS_REGION and C2PA_SIGNING_KEY_ARN were never read by anything."""
    assert not declared_variables() & {"DATABASE_URL", "AWS_REGION", "C2PA_SIGNING_KEY_ARN"}


def test_signing_material_falls_back_to_ephemeral_dev_certificates() -> None:
    """With nothing configured the repo still signs, which is why it runs keyless."""
    assert settings.c2pa_cert_path is None
    assert signing_material_from_settings().certificate_chain_pem.startswith(
        "-----BEGIN CERTIFICATE-----"
    )


def test_configured_signing_material_is_loaded_from_disk(tmp_path: Path) -> None:
    material = generate_dev_signing_material()
    cert = tmp_path / "chain.pem"
    key = tmp_path / "key.pem"
    cert.write_text(material.certificate_chain_pem, encoding="ascii")
    key.write_text(material.private_key_pem, encoding="ascii")

    loaded = load_signing_material(cert, key)
    assert loaded.certificate_chain_pem == material.certificate_chain_pem


def test_a_wrong_key_type_is_rejected_with_a_specific_message(tmp_path: Path) -> None:
    material = generate_dev_signing_material()
    cert = tmp_path / "chain.pem"
    cert.write_text(material.certificate_chain_pem, encoding="ascii")
    key = save_ledger_key(Ed25519PrivateKey.generate(), tmp_path / "ed.pem")

    with pytest.raises(ValueError, match="not an EC private key"):
        load_signing_material(cert, key)


def test_ledger_key_falls_back_to_an_ephemeral_key() -> None:
    assert settings.ledger_signing_key_path is None
    assert len(public_key_hex(ledger_key_from_settings())) == 64


def test_a_configured_ledger_key_gives_a_stable_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    key = Ed25519PrivateKey.generate()
    path = save_ledger_key(key, tmp_path / "ledger.pem")
    monkeypatch.setattr(settings, "ledger_signing_key_path", str(path))

    assert public_key_hex(ledger_key_from_settings()) == public_key_hex(key)


def test_the_tsa_url_is_read_from_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wiring only: the engine never fetches a token itself."""
    import inspect

    from attestor.provenance import signer as signer_module

    monkeypatch.setattr(settings, "rfc3161_tsa_url", "https://tsa.example/tsr")
    source = inspect.getsource(signer_module.build_signer)
    assert "settings.rfc3161_tsa_url" in source
