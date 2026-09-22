"""The append-only ledger: build it, seal it, write it, read it back.

The on-disk form is two files, deliberately:

- ``records.json``   the append-only entries, in order;
- ``signed_root.json`` the Merkle root over them, signed with Ed25519.

Two files rather than one because it makes the tamper story legible to a human:
edit a record and the recomputed root stops matching the sealed one, while the
signature over that sealed root still verifies. An auditor sees "the evidence was
edited after sealing", which is a different accusation from "the signature is bad".
"""

import json
from datetime import UTC, datetime
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from attestor.ledger.keys import public_key_hex
from attestor.ledger.merkle import merkle_root_of
from attestor.ledger.model import LEDGER_ALGORITHM, LedgerRecord, RecordTimestamp, SignedRoot

RECORDS_FILENAME = "records.json"
SIGNED_ROOT_FILENAME = "signed_root.json"


class LedgerError(ValueError):
    """Raised when a ledger cannot be built, sealed, or loaded."""


class Ledger:
    """An append-only sequence of records with a Merkle root over them."""

    def __init__(self, records: list[LedgerRecord] | None = None) -> None:
        self.records: list[LedgerRecord] = list(records or [])

    def append(
        self,
        *,
        id: str,
        kind: str,
        subject: str,
        payload_sha256: str,
        recorded_at: datetime | None = None,
    ) -> LedgerRecord:
        """Append one record and return it."""
        if any(r.id == id for r in self.records):
            raise LedgerError(f"duplicate record id: {id!r}")
        record = LedgerRecord(
            id=id,
            kind=kind,
            subject=subject,
            payload_sha256=payload_sha256,
            recorded_at=recorded_at or datetime.now(UTC),
        )
        self.records.append(record)
        return record

    @property
    def merkle_root(self) -> str:
        """The current RFC 6962 Merkle root over the appended records."""
        return merkle_root_of([r.canonical_bytes() for r in self.records])

    def seal(self, key: Ed25519PrivateKey, *, sealed_at: datetime | None = None) -> SignedRoot:
        """Sign the current Merkle root, producing the ledger's ``SignedRoot``."""
        if not self.records:
            raise LedgerError("refusing to seal an empty ledger")
        root = SignedRoot(
            merkle_root=self.merkle_root,
            leaf_count=len(self.records),
            algorithm=LEDGER_ALGORITHM,
            public_key=public_key_hex(key),
            signature="",
            sealed_at=sealed_at or datetime.now(UTC),
        )
        signature = key.sign(root.signed_payload())
        return root.model_copy(update={"signature": signature.hex()})


def attach_timestamp(root: SignedRoot, stamp: RecordTimestamp) -> SignedRoot:
    """Return ``root`` with an RFC3161 token attached.

    The token is attached after sealing because it timestamps the root; it can
    never be an input to the signature that produces it.
    """
    return root.model_copy(update={"timestamp": stamp})


def save_ledger(directory: str | Path, records: list[LedgerRecord], root: SignedRoot) -> Path:
    """Write ``records.json`` and ``signed_root.json`` into ``directory``."""
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    _write_json(target / RECORDS_FILENAME, [r.model_dump(mode="json") for r in records])
    _write_json(target / SIGNED_ROOT_FILENAME, root.model_dump(mode="json", exclude_none=True))
    return target


def load_ledger(directory: str | Path) -> tuple[list[LedgerRecord], SignedRoot]:
    """Read a ledger back from ``directory``. Raises ``OSError`` if files are missing."""
    source = Path(directory)
    raw_records = json.loads((source / RECORDS_FILENAME).read_text(encoding="utf-8"))
    raw_root = json.loads((source / SIGNED_ROOT_FILENAME).read_text(encoding="utf-8"))
    if not isinstance(raw_records, list):
        raise LedgerError(f"{RECORDS_FILENAME} must contain a JSON array")
    records = [LedgerRecord.model_validate(item) for item in raw_records]
    return records, SignedRoot.model_validate(raw_root)


def _write_json(path: Path, payload: object) -> None:
    # Trailing newline and sorted keys so the committed example is diff-friendly
    # and byte-stable across machines.
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
