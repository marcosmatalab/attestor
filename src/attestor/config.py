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


settings = Settings()
