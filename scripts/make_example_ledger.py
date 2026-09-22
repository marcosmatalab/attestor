"""Regenerate ``examples/ledger/`` from the engine.

The committed example exists so a third party can verify this repo's central
claim with one command and no Python. This script is what produces it, so the
artifact is never a file someone pasted in by hand.

The three anchored digests are all deterministic — the classification checksum,
the canonical Annex IV dossier, and the C2PA *manifest definition* (the manifest
as built from the classification, before signing). The signed asset is
deliberately not anchored here: ECDSA signing is randomised, so anchoring it
would make this script produce different records on every run for reasons that
say nothing about the engine.

The Ed25519 private key is generated into a temporary directory and never
written into the repository. Re-running this therefore produces a *different but
equally valid* signature and public key; the committed files keep verifying
regardless, which is the property that matters.

    python scripts/make_example_ledger.py [output_dir]
"""

import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from attestor import __version__
from attestor.annexiv import generate_dossier, validate_citations
from attestor.canonical import canonical_json, sha256_hex
from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle
from attestor.ledger import (
    Ledger,
    generate_ledger_key,
    save_ledger,
    save_ledger_key,
    verify_ledger,
)
from attestor.provenance import build_manifest

DEFAULT_OUTPUT = Path("examples/ledger")
SUBJECT = "sys-1"
SYSTEM_NAME = "ACME Recruiting Screener"
RECORDED_AT = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)


def build_example_ledger() -> Ledger:
    """Build the three-record example ledger from live engine output."""
    bundle = load_bundle()
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, bundle)

    dossier = generate_dossier(profile, classification, bundle, system_name=SYSTEM_NAME)
    validate_citations(dossier, classification, bundle)
    dossier_sha256 = sha256_hex(canonical_json(dossier.model_dump(mode="json")))

    manifest = build_manifest(classification, title="attestor-demo.png", version=__version__)
    manifest_sha256 = sha256_hex(canonical_json(manifest))

    ledger = Ledger()
    ledger.append(
        id="rec-1",
        kind="classification",
        subject=SUBJECT,
        payload_sha256=classification.checksum,
        recorded_at=RECORDED_AT,
    )
    ledger.append(
        id="rec-2",
        kind="annex-iv-dossier",
        subject=SUBJECT,
        payload_sha256=dossier_sha256,
        recorded_at=RECORDED_AT,
    )
    ledger.append(
        id="rec-3",
        kind="c2pa-manifest",
        subject=SUBJECT,
        payload_sha256=manifest_sha256,
        recorded_at=RECORDED_AT,
    )
    return ledger


def main(argv: list[str] | None = None) -> int:
    """Write the example ledger to the output directory (default ``examples/ledger``)."""
    args = list(sys.argv[1:] if argv is None else argv)
    output = Path(args[0]) if args else DEFAULT_OUTPUT

    ledger = build_example_ledger()
    key = generate_ledger_key()
    with tempfile.TemporaryDirectory() as scratch:
        # Written outside the repository, on purpose, and discarded with the scratch
        # directory: the example is verifiable with the public key alone.
        save_ledger_key(key, Path(scratch) / "ledger-key.pem")
        signed_root = ledger.seal(key, sealed_at=RECORDED_AT)

    save_ledger(output, ledger.records, signed_root)
    result = verify_ledger(ledger.records, signed_root)
    print(f"wrote {output} ({signed_root.leaf_count} records)")
    print(f"  merkle_root = {signed_root.merkle_root}")
    print(f"  public_key  = {signed_root.public_key}")
    print(f"  {result.detail}")
    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
