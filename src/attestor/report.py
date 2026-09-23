"""Serialize engine results for a caller, computed properties included.

The API and the CLI both hand engine output to someone else, and neither may
reimplement a verdict: ``headline``, ``verified`` and the rest are properties on the
engine models, so they are copied out verbatim. Living here rather than in ``api/``
means the CLI can use it without importing the web framework.
"""

from typing import Any

from pydantic import BaseModel

from attestor.ledger import LedgerVerification


def dump(model: BaseModel, **computed: Any) -> dict[str, Any]:
    """Serialize an engine model plus its computed properties, verbatim."""
    return {**model.model_dump(mode="json"), **computed}


def ledger_report(result: LedgerVerification) -> dict[str, Any]:
    """A ledger verification with every verdict the model computes."""
    return dump(
        result,
        headline=result.headline,
        verified=result.verified,
        tampered=result.tampered,
        untrusted_signer=result.untrusted_signer,
        signer_not_pinned=result.signer_not_pinned,
    )
