"""Versioned regulatory bundle: the data the engine interprets.

A bundle is the *interpretation* of the regulation, kept as versioned data rather
than hardcoded logic — so it can be audited, diffed, and superseded. F2 will add a
Digital Omnibus scenario as a separate bundle file, never a migration of this one.

Content-addressing: the bundle's identity is the SHA-256 of its canonical content,
not its version string. Editing any byte of meaning changes ``sha256`` and, in
turn, every classification checksum derived from it.
"""

import importlib.resources
from typing import Any

import yaml

from attestor.canonical import canonical_json, sha256_hex

DEFAULT_VERSION = "v2026-08"
_CLASSIFIER_PACKAGE = "attestor.classifier"
_REQUIRED_KEYS = ("meta", "articles", "risk_tier_rules", "obligation_rules", "obligations")


class Bundle:
    """A parsed, validated, content-addressed regulatory bundle."""

    def __init__(self, content: dict[str, Any]) -> None:
        self.content = content
        self._validate()
        self.sha256 = sha256_hex(canonical_json(content))

    @property
    def version(self) -> str:
        return self.content["meta"]["version"]

    @property
    def meta(self) -> dict[str, Any]:
        return self.content["meta"]

    @property
    def risk_tier_rules(self) -> list[dict[str, Any]]:
        return self.content["risk_tier_rules"]

    @property
    def obligation_rules(self) -> list[dict[str, Any]]:
        return self.content["obligation_rules"]

    @property
    def obligations(self) -> dict[str, dict[str, str]]:
        return self.content["obligations"]

    @property
    def articles(self) -> dict[str, str]:
        return self.content["articles"]

    def _validate(self) -> None:
        missing = [key for key in _REQUIRED_KEYS if key not in self.content]
        if missing:
            raise ValueError(f"bundle missing top-level keys: {missing}")

        obligations = self.content["obligations"]
        articles = self.content["articles"]

        for rule in self.content["obligation_rules"]:
            oid = rule.get("obligation")
            if oid not in obligations:
                raise ValueError(f"obligation_rule references unknown obligation: {oid!r}")
            if "effective_date" not in rule:
                raise ValueError(f"obligation_rule for {oid!r} is missing effective_date")

        # Every reference must resolve in the article index — this is the invariant
        # the F3 citation validator will rely on (no obligation with a dangling cite).
        for oid, meta in obligations.items():
            ref = meta.get("reference")
            if ref not in articles:
                raise ValueError(f"obligation {oid!r} has unresolved reference: {ref!r}")


def load_bundle(version: str = DEFAULT_VERSION) -> Bundle:
    """Load and validate the bundle for ``version`` from packaged resources."""
    resource = (
        importlib.resources.files(_CLASSIFIER_PACKAGE).joinpath("rules").joinpath(f"{version}.yaml")
    )
    content = yaml.safe_load(resource.read_text(encoding="utf-8"))
    return Bundle(content)
