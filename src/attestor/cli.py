"""``attestor`` — the command line a reviewer actually runs.

Three subcommands over the engine that already exists, added so that verifying
this repo's central claim takes one command instead of a Python snippet:

- ``attestor classify``      reproduce a classification checksum;
- ``attestor ledger verify`` verify a ledger offline;
- ``attestor demo``          run the whole pipeline, no keys, no network.

Exit codes are part of the contract, not decoration, and ``ledger verify`` keeps
the ones ``python -m attestor.ledger`` already published: ``0`` verified, ``1``
tampered, ``2`` usage or I/O error. A script that cannot tell "the evidence was
edited" from "I could not read the file" is not a check.
"""

import argparse
import json
import sys
from typing import Any

from attestor import __version__
from attestor.classifier import SystemProfile, classify, load_bundle
from attestor.classifier.bundle import DEFAULT_VERSION, available_versions
from attestor.classifier.model import AnnexIIIArea, ContentLifecycle, DeployerType, Role
from attestor.ledger.__main__ import EXIT_TAMPERED, EXIT_USAGE, EXIT_VERIFIED
from attestor.ledger.__main__ import main as ledger_main

PROGRAM = "attestor"


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog=PROGRAM,
        description="Deterministic EU AI Act compliance engine.",
    )
    parser.add_argument("--version", action="version", version=f"{PROGRAM} {__version__}")
    subcommands = parser.add_subparsers(dest="command", required=True)

    classify_parser = subcommands.add_parser(
        "classify", help="classify a system profile and print the result"
    )
    classify_parser.add_argument(
        "--role", required=True, choices=[r.value for r in Role], help="provider or deployer"
    )
    classify_parser.add_argument(
        "--annex-iii-area", choices=[a.value for a in AnnexIIIArea], help="Annex III high-risk area"
    )
    classify_parser.add_argument(
        "--deployer-type",
        choices=[d.value for d in DeployerType],
        help="deployer category (Art. 27)",
    )
    classify_parser.add_argument(
        "--annex-i-embedded", action="store_true", help="embedded in an Annex I product"
    )
    classify_parser.add_argument(
        "--interacts-with-humans", action="store_true", help="Art. 50(1) trigger"
    )
    classify_parser.add_argument(
        "--generates-synthetic-content", action="store_true", help="Art. 50(2) trigger"
    )
    classify_parser.add_argument(
        "--content-lifecycle",
        choices=[c.value for c in ContentLifecycle],
        help="new or legacy synthetic content (required with --generates-synthetic-content)",
    )
    classify_parser.add_argument(
        "--bundle",
        default=DEFAULT_VERSION,
        help=(
            f"regulatory bundle (default: {DEFAULT_VERSION}; "
            f"available: {', '.join(available_versions())})"
        ),
    )
    classify_parser.add_argument(
        "--checksum-only", action="store_true", help="print only the classification checksum"
    )

    ledger_parser = subcommands.add_parser("ledger", help="ledger operations")
    ledger_sub = ledger_parser.add_subparsers(dest="ledger_command", required=True)
    verify_parser = ledger_sub.add_parser("verify", help="verify a ledger directory offline")
    verify_parser.add_argument("directory", help="e.g. examples/ledger")

    demo_parser = subcommands.add_parser(
        "demo", help="run the full pipeline end to end (no keys, no network)"
    )
    demo_parser.add_argument("--json", action="store_true", help="print the raw JSON report")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``attestor`` console script."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "classify":
        return _run_classify(args)
    if args.command == "ledger":
        return ledger_main([args.directory])
    if args.command == "demo":
        return _run_demo(args)
    parser.error(f"unknown command: {args.command!r}")  # pragma: no cover - argparse guards this
    return EXIT_USAGE  # pragma: no cover


def _run_classify(args: argparse.Namespace) -> int:
    try:
        bundle = load_bundle(args.bundle)
    except (FileNotFoundError, ValueError) as exc:
        print(f"could not load bundle {args.bundle!r}: {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        profile = SystemProfile(
            role=Role(args.role),
            annex_iii_area=AnnexIIIArea(args.annex_iii_area) if args.annex_iii_area else None,
            deployer_type=DeployerType(args.deployer_type) if args.deployer_type else None,
            annex_i_embedded=args.annex_i_embedded,
            interacts_with_humans=args.interacts_with_humans,
            generates_synthetic_content=args.generates_synthetic_content,
            content_lifecycle=(
                ContentLifecycle(args.content_lifecycle) if args.content_lifecycle else None
            ),
        )
    except ValueError as exc:
        print(f"invalid profile: {exc}", file=sys.stderr)
        return EXIT_USAGE

    result = classify(profile, bundle)
    if args.checksum_only:
        print(result.checksum)
        return EXIT_VERIFIED

    print(f"risk       {result.risk.value}")
    print(f"bundle     {result.bundle_version} (sha256 {result.bundle_sha256})")
    print(f"checksum   {result.checksum}")
    print("obligations:")
    for obligation in result.obligations:
        print(f"  {obligation.effective_date}  {obligation.reference:<12} {obligation.title}")
    return EXIT_VERIFIED


def _run_demo(args: argparse.Namespace) -> int:
    from attestor.demo import run_demo

    report: dict[str, Any] = run_demo()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return EXIT_VERIFIED

    classification = report["classification"]
    provenance = report["provenance"]
    ledger = report["ledger"]
    print(f"classification  risk={classification['risk']} checksum={classification['checksum']}")
    print(f"bundle          {report['bundle']['version']} sha256={report['bundle']['sha256']}")
    print(f"annex IV        {report['annex_iv']['citation_count']} validated citations")
    print(f"C2PA            {provenance['headline']}")
    print(f"ledger          {ledger['verification']['detail']}")
    print(f"                merkle_root={ledger['signed_root']['merkle_root']}")
    return EXIT_VERIFIED if ledger["verification"]["verified"] else EXIT_TAMPERED


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess in tests
    raise SystemExit(main())
