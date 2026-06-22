"""Determinism tests: reproducibility of the full output, and sensitivity.

These certify what the checksum is supposed to mean: the *engine* is deterministic
(same input + bundle -> identical Classification), and a relevant change to either
the input or the bundle changes the OUTPUT, not merely the checksum.
"""

import copy

from attestor.classifier import (
    AnnexIIIArea,
    Bundle,
    DeployerType,
    Role,
    SystemProfile,
    classify,
    load_bundle,
)


def test_full_classification_is_reproducible() -> None:
    bundle = load_bundle()
    profile = SystemProfile(
        role=Role.deployer,
        annex_iii_area=AnnexIIIArea.credit_scoring,
        deployer_type=DeployerType.other,
    )

    first = classify(profile, bundle)
    second = classify(profile, bundle)

    # Full object equality: risk + obligations + dates + checksum.
    assert first == second
    assert first.checksum == second.checksum


def test_relevant_input_change_changes_the_output() -> None:
    bundle = load_bundle()
    minimal = classify(SystemProfile(role=Role.provider), bundle)
    high = classify(
        SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment), bundle
    )

    # The output itself differs, not just the checksum.
    assert minimal.risk != high.risk
    assert minimal.obligations != high.obligations
    assert minimal.checksum != high.checksum


def test_bundle_change_flows_into_output_and_checksum() -> None:
    bundle = load_bundle()
    profile = SystemProfile(role=Role.provider, annex_iii_area=AnnexIIIArea.employment)
    before = classify(profile, bundle)

    mutated_content = copy.deepcopy(bundle.content)
    for rule in mutated_content["obligation_rules"]:
        if rule["obligation"] == "art9_risk_management" and rule["when"].get("has_annex_iii_area"):
            rule["effective_date"] = "2099-01-01"
    mutated = Bundle(mutated_content)
    after = classify(profile, mutated)

    assert mutated.sha256 != bundle.sha256
    assert after.effective_dates["art9_risk_management"] == "2099-01-01"
    assert after.checksum != before.checksum
