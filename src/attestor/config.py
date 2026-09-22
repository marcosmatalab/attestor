"""Application configuration.

Only settings the code actually reads. A variable that nothing reads does not belong
in a config class or in ``.env.example``: it reads as a capability the project has
and does not.

Key material is referenced **by path**, never by value. That path is the seam: a KMS
or HSM signer would replace the loader that reads it, and nothing else. No such
backend is implemented here.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, loaded from environment variables and an optional ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"

    # C2PA provenance signing (F4). Paths to a PEM certificate chain (leaf + CA) and
    # the leaf private key. NEVER hardcoded or committed; with both unset a
    # self-signed dev chain is generated, which is why the repo signs with no keys.
    # Replacing the loader that reads these paths is what a KMS/HSM signer would
    # change. The TSA URL (RFC3161) is optional and shared with the ledger (F6).
    c2pa_cert_path: str | None = None
    c2pa_private_key_path: str | None = None
    rfc3161_tsa_url: str | None = None

    # Cryptographic ledger (F6). Path to the Ed25519 private key that signs Merkle
    # roots; never hardcoded or committed — the public key is published instead, and
    # offline verification needs only the public key. The path is config-driven; a
    # KMS/HSM signer would replace this loader. The TSA URL above (RFC3161_TSA_URL)
    # is reused to timestamp roots.
    ledger_signing_key_path: str | None = None


settings = Settings()
