"""Offline ledger verifier CLI: ``python -m attestor.ledger <ledger_dir>``.

Consumes only PUBLIC artifacts (``records.json``, ``signed_root.json``, and optional
``tsa/leaf.pem`` + ``tsa/root.pem``) — no network and no private key. Exit 0 if the
ledger is intact and signed; exit 1 if tampering is detected. TSA trust is reported but
NEVER drives the exit code: a valid ledger timestamped by an unrecognised TSA is exit 0.
"""

import sys
from pathlib import Path

from cryptography import x509

from attestor.ledger.ledger import load_ledger
from attestor.ledger.verifier import verify_ledger

_USAGE = "usage: python -m attestor.ledger <ledger_dir>"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print(_USAGE, file=sys.stderr)
        return 2

    directory = Path(args[0])
    try:
        records, signed_root = load_ledger(directory)
    except (FileNotFoundError, ValueError) as exc:
        print(f"could not load ledger from {directory}: {exc}", file=sys.stderr)
        return 2

    tsa_leaf = tsa_root = None
    leaf_path, root_path = directory / "tsa" / "leaf.pem", directory / "tsa" / "root.pem"
    if leaf_path.is_file() and root_path.is_file():
        tsa_leaf = x509.load_pem_x509_certificate(leaf_path.read_bytes())
        tsa_root = x509.load_pem_x509_certificate(root_path.read_bytes())

    result = verify_ledger(records, signed_root, tsa_leaf=tsa_leaf, tsa_root=tsa_root)
    print(result.headline)
    print(f"  integrity_ok = {result.integrity_ok}")
    print(f"  signature_ok = {result.signature_ok}")
    if result.has_timestamp:
        print(f"  timestamp_ok = {result.timestamp_ok}   tsa_trusted = {result.tsa_trusted}")
    # Exit code is the TAMPER check only — never TSA trust.
    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
