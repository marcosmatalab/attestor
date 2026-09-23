"""Offline ledger verifier CLI: ``python -m attestor.ledger <ledger_dir> [--public-key FILE]``.

Consumes only PUBLIC artifacts (``records.json``, ``signed_root.json``, and optional
``tsa/leaf.pem`` + ``tsa/root.pem``) — no network and no private key.

Exit codes are a contract:

- ``0`` intact and signed (and, with ``--public-key``, signed by that key);
- ``1`` tampered: the records or the signed root do not hold together;
- ``2`` usage or I/O error;
- ``3`` untrusted signer: intact and signed, but NOT by the pinned key.

``3`` exists because a ledger re-sealed by someone else is internally consistent: the
signature is checked with the key stored next to it. Only a pinned key tells "sealed by
the operator" apart from "sealed by whoever edited the records". TSA trust is reported
but NEVER drives the exit code: a valid ledger timestamped by an unrecognised TSA is 0.
"""

import argparse
import sys
from pathlib import Path

from cryptography import x509

from attestor.ledger.keys import load_pinned_public_key
from attestor.ledger.ledger import load_ledger
from attestor.ledger.verifier import verify_ledger

EXIT_OK = 0
EXIT_TAMPERED = 1
EXIT_USAGE = 2
EXIT_UNTRUSTED_SIGNER = 3

PUBLIC_KEY_HELP = (
    "Ed25519 public key the ledger must be signed with (PEM or 64 hex characters); "
    "without it the signature is only checked against the key the ledger carries"
)


def add_verify_arguments(parser: argparse.ArgumentParser) -> None:
    """The arguments both entry points share, so they cannot drift apart."""
    parser.add_argument("directory", help="ledger directory, e.g. examples/ledger")
    parser.add_argument("--public-key", metavar="FILE", help=PUBLIC_KEY_HELP)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m attestor.ledger", description="Verify a ledger offline."
    )
    add_verify_arguments(parser)
    try:
        args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as exc:  # argparse exits 2 on bad usage; keep it a return value
        return EXIT_USAGE if exc.code else EXIT_OK
    return verify_directory(Path(args.directory), args.public_key)


def verify_directory(directory: Path, public_key: str | None = None) -> int:
    """Verify ``directory``, print the verdict and return the exit code."""
    expected = None
    if public_key is not None:
        try:
            expected = load_pinned_public_key(public_key)
        except (OSError, ValueError) as exc:
            print(f"could not load public key from {public_key}: {exc}", file=sys.stderr)
            return EXIT_USAGE

    try:
        records, signed_root = load_ledger(directory)
    except (FileNotFoundError, ValueError) as exc:
        print(f"could not load ledger from {directory}: {exc}", file=sys.stderr)
        return EXIT_USAGE

    tsa_leaf = tsa_root = None
    leaf_path, root_path = directory / "tsa" / "leaf.pem", directory / "tsa" / "root.pem"
    if leaf_path.is_file() and root_path.is_file():
        tsa_leaf = x509.load_pem_x509_certificate(leaf_path.read_bytes())
        tsa_root = x509.load_pem_x509_certificate(root_path.read_bytes())

    result = verify_ledger(
        records, signed_root, tsa_leaf=tsa_leaf, tsa_root=tsa_root, expected_public_key=expected
    )
    print(result.headline)
    print(f"  integrity_ok = {result.integrity_ok}")
    print(f"  signature_ok = {result.signature_ok}")
    print(f"  signer_sha256 = {result.signer_fingerprint}")
    if result.signer_pinned:
        print(f"  signer_pinned = True   matches = {result.signer_matches_pin}")
    if result.has_timestamp:
        print(f"  timestamp_ok = {result.timestamp_ok}   tsa_trusted = {result.tsa_trusted}")
    # Tampering outranks a foreign signer; TSA trust never moves the exit code.
    if result.tampered:
        return EXIT_TAMPERED
    if result.untrusted_signer:
        return EXIT_UNTRUSTED_SIGNER
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
