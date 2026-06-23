"""Application configuration.

Minimal scaffold for F0: only the settings needed to boot the service. Domain
configuration (regulatory bundles, KMS keys, TSA endpoints, ledger keys) is
introduced in later phases. ``extra="ignore"`` lets a ``.env`` file already carry
those future variables without breaking the F0 boot.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, loaded from environment variables and an optional ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # C2PA provenance signing (F4). Paths to a PEM certificate chain (leaf + CA)
    # and the leaf private key. NEVER hardcoded or committed; in dev a self-signed
    # chain is generated, in production the key lives in a KMS/HSM. The TSA URL
    # (RFC3161) is optional and shared with the ledger (F6).
    c2pa_cert_path: str | None = None
    c2pa_private_key_path: str | None = None
    rfc3161_tsa_url: str | None = None

    # Cryptographic ledger (F6). Path to the Ed25519 private key that signs Merkle
    # roots; never hardcoded or committed — the public key is published instead, and
    # offline verification needs only the public key. In production the key lives in
    # a KMS/HSM. The TSA URL above (RFC3161_TSA_URL) is reused to timestamp roots.
    ledger_signing_key_path: str | None = None


settings = Settings()
