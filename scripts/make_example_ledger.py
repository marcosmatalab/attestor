"""Regenerate ``examples/ledger/`` from the engine.

The committed example exists so a third party can check this repository's central
claim with one command and no Python. This script produces it, so the artifact is
never a file someone pasted in by hand.

All three anchored digests are deterministic: the classification checksum, the
canonical Annex IV dossier, and the C2PA **manifest definition** (the manifest as
built from metadata, before signing). The *signed asset* is deliberately not
anchored here: ECDSA signing is randomised and the dev certificate is ephemeral, so
anchoring it would make this script emit different records on every run for reasons
that say nothing about the engine. The API demo anchors the signed asset instead,
because there the point is the live pipeline rather than a stable artifact.

The Ed25519 private key is generated into a temporary directory and never written
into the repository. Re-running therefore mints a new key and produces a different
- and equally valid - signature; the committed files keep verifying regardless,
which is the property that matters. The matching public key is written next to them
as ``public_key.pem`` so a verifier can pin it (``--public-key``); a re-run replaces
it, and the fingerprint quoted in ``examples/ledger/README.md`` must then be updated,
which ``tests/test_ledger_signer_pinning.py`` enforces.

    python scripts/make_example_ledger.py [output_dir]
"""

import sys
import tempfile
from pathlib import Path
from typing import Any

from attestor.annexiv import generate_dossier, validate_citations
from attestor.canonical import canonical_json, sha256_hex
from attestor.classifier import AnnexIIIArea, Role, SystemProfile, classify, load_bundle
from attestor.ledger import (
    Ledger,
    generate_ledger_key,
    load_private_key,
    save_ledger,
    verify_ledger,
)
from attestor.ledger.keys import public_key_fingerprint, public_key_pem
from attestor.provenance import ProvenanceMetadata, build_manifest

DEFAULT_OUTPUT = Path("examples/ledger")
SUBJECT = "sys-1"
SYSTEM_NAME = "ACME Recruiting Screener"


def build_records() -> list[dict[str, Any]]:
    """The three deterministic records the example anchors."""
    bundle = load_bundle()
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    classification = classify(profile, bundle)

    dossier = generate_dossier(profile, classification, bundle, system_name=SYSTEM_NAME)
    validate_citations(dossier, classification, bundle)
    dossier_sha256 = sha256_hex(canonical_json(dossier.model_dump(mode="json")))

    manifest = build_manifest(ProvenanceMetadata(title="attestor-demo.png", model="attestor-demo"))
    manifest_sha256 = sha256_hex(canonical_json(manifest))

    return [
        {
            "type": "classification",
            "system": SUBJECT,
            "bundle": classification.bundle_version,
            "bundle_sha256": classification.bundle_sha256,
            "checksum": classification.checksum,
        },
        {
            "type": "annex_iv",
            "system": SUBJECT,
            "classification_checksum": classification.checksum,
            "dossier_sha256": dossier_sha256,
        },
        {
            "type": "c2pa_manifest",
            "system": SUBJECT,
            "sha256": manifest_sha256,
        },
    ]


def write_public_key(output: Path, public_key_hex: str) -> Path:
    """Publish the verifying key as ``public_key.pem``, the file ``--public-key`` pins."""
    path = output / "public_key.pem"
    path.write_bytes(public_key_pem(public_key_hex))
    return path


def main(argv: list[str] | None = None) -> int:
    """Write the example ledger to the output directory (default ``examples/ledger``)."""
    args = list(sys.argv[1:] if argv is None else argv)
    output = Path(args[0]) if args else DEFAULT_OUTPUT

    records = build_records()

    with tempfile.TemporaryDirectory() as scratch:
        # Written outside the repository, on purpose, and discarded with the scratch
        # directory: the example is verifiable from public material alone.
        key_path = Path(scratch) / "ledger.key"
        generate_ledger_key(key_path)
        signed_root = Ledger(records).seal(load_private_key(key_path))

    save_ledger(output, records, signed_root)
    write_public_key(output, signed_root.public_key)
    result = verify_ledger(records, signed_root, expected_public_key=signed_root.public_key)

    print(f"wrote {output} ({signed_root.leaf_count} records)")
    print(f"  merkle_root = {signed_root.merkle_root}")
    print(f"  public_key  = {signed_root.public_key}")
    print(f"  signer_sha256 = {public_key_fingerprint(signed_root.public_key)}")
    print(f"  {result.headline}")
    return 0 if result.verified else 1


if __name__ == "__main__":
    raise SystemExit(main())
