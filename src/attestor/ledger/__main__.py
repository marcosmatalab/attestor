"""``python -m attestor.ledger <dir>`` — verify a ledger offline.

Exit codes are the interface; they are what a CI job or an auditor's script reads:

- ``0`` verified,
- ``1`` tampered (the files parsed, the verdict is negative),
- ``2`` usage or I/O error (there was nothing to verify).

Keeping "tampered" and "could not read it" on different codes matters: a script
that treats a missing file as a passing ledger is worse than no check at all.
"""

import sys
from pathlib import Path

from attestor.ledger.ledger import load_ledger
from attestor.ledger.verifier import verify_ledger

EXIT_VERIFIED = 0
EXIT_TAMPERED = 1
EXIT_USAGE = 2

USAGE = (
    "usage: python -m attestor.ledger <ledger_dir>\n"
    "  e.g. python -m attestor.ledger examples/ledger   "
    "(a committed, verifiable ledger ships with this repo)"
)


def main(argv: list[str] | None = None) -> int:
    """Verify the ledger directory given on the command line."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 1 or args[0] in {"-h", "--help"}:
        print(USAGE, file=sys.stderr)
        return EXIT_USAGE

    directory = Path(args[0])
    try:
        records, root = load_ledger(directory)
    except (OSError, ValueError) as exc:
        print(f"could not load ledger from {args[0]}: {exc}", file=sys.stderr)
        return EXIT_USAGE

    result = verify_ledger(records, root)
    print(result.detail)
    print(f"  integrity_ok = {result.integrity_ok}")
    print(f"  signature_ok = {result.signature_ok}")
    if result.timestamp_ok is not None:
        print(f"  timestamp_ok = {result.timestamp_ok}")
    return EXIT_VERIFIED if result.verified else EXIT_TAMPERED


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess in tests
    raise SystemExit(main())
