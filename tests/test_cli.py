"""The ``attestor`` CLI: output a reviewer copies, and exit codes a script reads."""

from pathlib import Path

import pytest

from attestor.cli import main

# Literal digests, one per scenario. They are the repository's central claim, so a
# change to canonicalisation has to be typed here deliberately rather than slip past.
IN_FORCE_EMPLOYMENT = "d821e3e0b95d4edda4416916f2a5b02ef0296f34704a0010ee0222b3a9e0ee48"
LEGAL_TEXT_EMPLOYMENT = "15815cd8f577dea7cc09696acc9a3e96870664573ea428e7c81bb8b06a84bd17"
OMNIBUS_EMPLOYMENT = "3bc20cb8a68d47c16d36c91a400acd2e0b03eb2020f2983a14bdfc7a56fe24f0"
EXAMPLE_LEDGER = str(Path(__file__).resolve().parents[1] / "examples" / "ledger")


def test_checksum_only_prints_exactly_the_checksum(capsys) -> None:
    code = main(
        ["classify", "--role", "provider", "--annex-iii-area", "employment", "--checksum-only"]
    )
    assert code == 0
    assert capsys.readouterr().out.strip() == IN_FORCE_EMPLOYMENT


def test_checksum_is_the_same_on_a_second_run(capsys) -> None:
    """Determinism is the claim; running it twice is the proof."""
    outputs = []
    for _ in range(2):
        main(
            ["classify", "--role", "provider", "--annex-iii-area", "employment", "--checksum-only"]
        )
        outputs.append(capsys.readouterr().out.strip())
    assert outputs[0] == outputs[1] == IN_FORCE_EMPLOYMENT


@pytest.mark.parametrize(
    ("bundle", "expected"),
    [("v2026-08", LEGAL_TEXT_EMPLOYMENT), ("omnibus-2026", OMNIBUS_EMPLOYMENT)],
)
def test_bundle_flag_selects_the_scenario(bundle: str, expected: str, capsys) -> None:
    """Each frozen scenario still reproduces the digest it produced in June 2026."""
    main(
        [
            "classify",
            "--role",
            "provider",
            "--annex-iii-area",
            "employment",
            "--bundle",
            bundle,
            "--checksum-only",
        ]
    )
    assert capsys.readouterr().out.strip() == expected


def test_full_classify_output_lists_obligations_with_dates(capsys) -> None:
    assert main(["classify", "--role", "provider", "--annex-iii-area", "employment"]) == 0
    out = capsys.readouterr().out

    assert "risk       high" in out
    assert IN_FORCE_EMPLOYMENT in out
    assert "Art. 9" in out


def test_unknown_bundle_exits_with_the_usage_code(capsys) -> None:
    assert main(["classify", "--role", "provider", "--bundle", "nope", "--checksum-only"]) == 2
    assert "could not load bundle" in capsys.readouterr().err


def test_invalid_profile_combination_exits_with_the_usage_code(capsys) -> None:
    # generates_synthetic_content requires content_lifecycle.
    code = main(["classify", "--role", "provider", "--generates-synthetic-content"])
    assert code == 2
    assert "invalid profile" in capsys.readouterr().err


def test_ledger_verify_accepts_the_committed_example(capsys) -> None:
    assert main(["ledger", "verify", EXAMPLE_LEDGER]) == 0
    out = capsys.readouterr().out

    assert out.startswith("ledger VERIFIED")
    assert "integrity_ok = True" in out
    assert "signature_ok = True" in out


def test_ledger_verify_reports_tampering_with_exit_1(tmp_path: Path, capsys) -> None:
    source = Path(EXAMPLE_LEDGER)
    (tmp_path / "records.json").write_text(
        (source / "records.json").read_text(encoding="utf-8").replace("sys-1", "sys-9"),
        encoding="utf-8",
    )
    (tmp_path / "signed_root.json").write_text(
        (source / "signed_root.json").read_text(encoding="utf-8"), encoding="utf-8"
    )

    assert main(["ledger", "verify", str(tmp_path)]) == 1
    assert "TAMPERED" in capsys.readouterr().out


def test_missing_ledger_is_a_usage_error_not_a_pass(tmp_path: Path, capsys) -> None:
    """Exit 2, never 0: a missing file must never read as a verified ledger."""
    assert main(["ledger", "verify", str(tmp_path / "absent")]) == 2
    assert "could not load ledger" in capsys.readouterr().err


def test_demo_prints_both_provenance_axes_and_verifies(capsys) -> None:
    assert main(["demo"]) == 0
    out = capsys.readouterr().out

    assert IN_FORCE_EMPLOYMENT in out
    assert "integrity Valid" in out
    assert "signer UNTRUSTED" in out
    assert "ledger VERIFIED" in out


def test_demo_json_is_machine_readable(capsys) -> None:
    import json

    assert main(["demo", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)

    assert report["classification"]["checksum"] == IN_FORCE_EMPLOYMENT
    assert report["ledger"]["verification"]["verified"] is True


def test_no_subcommand_is_an_argparse_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2
