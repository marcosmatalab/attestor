"""Every configuration variable must be read by something.

An unread variable in `.env.example` advertises a capability the project does not
have, which is the same failure as a README claim with no code behind it. And
``extra="ignore"`` means it fails silently: the variable is simply swallowed, so
nothing ever complains. `DATABASE_URL`, `AWS_REGION` and `C2PA_SIGNING_KEY_ARN`
sat there for months that way. This test is what stops one creeping back in.
"""

import re
from pathlib import Path

from attestor.config import Settings

ENV_EXAMPLE = Path(__file__).resolve().parents[1] / ".env.example"
SRC = Path(__file__).resolve().parents[1] / "src" / "attestor"

# Variables that were declared and read by nothing, before this test existed.
GHOSTS = {"DATABASE_URL", "AWS_REGION", "C2PA_SIGNING_KEY_ARN"}


def declared_variables() -> set[str]:
    return {
        line.split("=", 1)[0].strip()
        for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }


def test_env_example_declares_exactly_what_settings_reads() -> None:
    assert declared_variables() == {name.upper() for name in Settings.model_fields}


def test_no_ghost_variables_from_abandoned_plans() -> None:
    assert not declared_variables() & GHOSTS


def test_no_ghost_variable_is_referenced_anywhere_in_the_engine() -> None:
    sources = "\n".join(p.read_text(encoding="utf-8") for p in SRC.rglob("*.py"))
    for ghost in GHOSTS:
        assert ghost not in sources
        assert ghost.lower() not in sources


def test_key_material_is_referenced_by_path_never_by_value() -> None:
    """The seam is a path. A field holding a key itself would be a different design."""
    for name in ("c2pa_cert_path", "c2pa_private_key_path", "ledger_signing_key_path"):
        assert name in Settings.model_fields
        assert name.endswith("_path")


def test_every_path_setting_is_actually_consumed_outside_config() -> None:
    """A field nothing reads is the same sin as a variable nothing reads."""
    sources = "\n".join(
        p.read_text(encoding="utf-8") for p in SRC.rglob("*.py") if p.name != "config.py"
    )
    for name in ("c2pa_cert_path", "c2pa_private_key_path", "ledger_signing_key_path"):
        assert re.search(rf"settings\.{name}\b", sources), f"{name} is never read"


def test_signing_defaults_to_keyless_so_the_repo_runs_from_a_clean_clone() -> None:
    settings = Settings()
    assert settings.c2pa_cert_path is None
    assert settings.c2pa_private_key_path is None
    assert settings.ledger_signing_key_path is None
    assert settings.rfc3161_tsa_url is None
