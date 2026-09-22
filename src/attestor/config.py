"""Application configuration.

Only settings the code actually reads. Every field here is used somewhere; a
variable that nothing reads does not belong in a config class, because it reads
as a capability the project has and does not.

Key material is referenced **by path**, never by value. That path is the seam: a
KMS or HSM signer would replace the loader that reads it, and nothing else. No
such backend is implemented here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, loaded from environment variables and an optional ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # C2PA signing material. Both default to None: the demo and the test suite mint
    # ephemeral development certificates instead, so the repository runs with no
    # keys and no network.
    c2pa_cert_path: str | None = None
    c2pa_private_key_path: str | None = None

    # RFC3161 timestamping authority. Optional by design: the engine performs no
    # network I/O, so a caller at the edge fetches the token and hands it in.
    rfc3161_tsa_url: str | None = None

    # Ed25519 key that seals the ledger.
    ledger_signing_key_path: str | None = None


settings = Settings()
