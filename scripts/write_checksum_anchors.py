"""Regenerate ``tests/golden/checksums.yaml``.

Run this ONLY when a change to canonicalisation or to a bundle is intended. The
anchors exist to make that change deliberate, so regenerating them without reading
the diff defeats the point of having them.

    python scripts/write_checksum_anchors.py
"""

import io
import pathlib

from attestor.classifier import SystemProfile, classify, load_bundle

OUTPUT = pathlib.Path(__file__).resolve().parents[1] / "tests" / "golden" / "checksums.yaml"

BUNDLES = ["v2026-08", "omnibus-2026", "reg-2026-1744"]

PROFILES: dict[str, dict[str, object]] = {
    "provider_annex_iii_employment": {"role": "provider", "annex_iii_area": "employment"},
    "provider_annex_i_embedded": {"role": "provider", "annex_i_embedded": True},
    "deployer_public_body_employment": {
        "role": "deployer",
        "annex_iii_area": "employment",
        "deployer_type": "public_body",
    },
    "deployer_other_employment": {
        "role": "deployer",
        "annex_iii_area": "employment",
        "deployer_type": "other",
    },
    "provider_chatbot_only": {"role": "provider", "interacts_with_humans": True},
    "provider_legacy_synthetic_content": {
        "role": "provider",
        "generates_synthetic_content": True,
        "content_lifecycle": "legacy",
    },
    "provider_gpai_systemic": {"role": "provider", "is_gpai": True, "is_gpai_systemic": True},
    "provider_ncii_no_safeguards": {"role": "provider", "generates_ncii_or_csam": True},
}

HEADER = """# Anchored digests. Literal values, checked by tests/test_checksum_anchors.py.
#
# WHY THIS FILE EXISTS. The golden vectors pin risk tiers and effective dates, and
# the determinism tests compare a run against itself - so a change to the canonical
# form would have sailed through the whole suite while the README promised auditors
# a reproducible checksum. Nothing anchored an actual digest. This does.
#
# It is deliberately annoying: any legitimate change to canonicalisation or to a
# bundle forces someone to retype these by hand. That decision is currently taken
# by accident, and it should not be.
#
# Regenerate (only when the change is intended):
#   python scripts/write_checksum_anchors.py

bundles:
"""


def _render_input(profile: dict[str, object]) -> str:
    parts = [
        f"{key}: {str(value).lower() if isinstance(value, bool) else value}"
        for key, value in profile.items()
    ]
    return "{ " + ", ".join(parts) + " }"


def render() -> str:
    """Build the YAML text from live engine output."""
    out = io.StringIO()
    out.write(HEADER)
    for version in BUNDLES:
        out.write(f'  {version}: "{load_bundle(version).sha256}"\n')

    out.write(
        "\n# Each profile is classified under all three scenario bundles. Same "
        "questionnaire,\n# three timelines, three distinct digests.\nclassifications:\n"
    )
    for name, profile in PROFILES.items():
        out.write(f"  {name}:\n    input: {_render_input(profile)}\n    expected:\n")
        for version in BUNDLES:
            checksum = classify(SystemProfile(**profile), load_bundle(version)).checksum
            out.write(f'      {version}: "{checksum}"\n')
    return out.getvalue()


def main() -> int:
    OUTPUT.write_text(render(), encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
